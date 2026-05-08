import sqlite3

# ─────────────────────────────────────────────
# CONEXIÓN
# ─────────────────────────────────────────────
from database import conectar

# ─────────────────────────────────────────────
# FUNCIÓN AUXILIAR - OBTENER PRÉSTAMO POR ID
# ─────────────────────────────────────────────

def obtener_prestamo_por_id(prestamo_id):
    """
    Obtiene un préstamo por su ID.
    Retorna el préstamo como un objeto Row o None si no existe.
    """
    conexion = conectar()
    if conexion is None:
        return None
    
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM prestamos WHERE id = ?", (prestamo_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"[ERROR] No se pudo obtener el préstamo: {e}")
        return None
    finally:
        cursor.close()
        conexion.close()

# ─────────────────────────────────────────────
# CRUD - CREAR PRÉSTAMO
# ─────────────────────────────────────────────

def crear_prestamo(libro_id, usuario, fecha):
    """
    Crea un nuevo préstamo para un libro.
    Comprueba que el libro exista y esté disponible antes de insertar.
    Actualiza la disponibilidad del libro a 0 (no disponible).
    """
    conexion = conectar()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()

        # Comprobar si el libro existe
        cursor.execute("SELECT id, titulo, disponible FROM libros WHERE id = ?", (libro_id,))
        libro = cursor.fetchone()

        if libro is None:
            print(f"[ERROR] No existe ningún libro con id {libro_id}.")
            return

        # Comprobar si el libro está disponible
        if libro["disponible"] == 0:
            print(f"[ERROR] El libro '{libro['titulo']}' no está disponible actualmente.")
            return

        # Insertar el préstamo
        cursor.execute(
            "INSERT INTO prestamos (libro_id, usuario, fecha_prestamo, fecha_devolucion, estado) "
            "VALUES (?, ?, ?, NULL, 'activo')",
            (libro_id, usuario, fecha)
        )

        # Marcar el libro como no disponible
        cursor.execute("UPDATE libros SET disponible = 0 WHERE id = ?", (libro_id,))

        conexion.commit()
        print(f"[OK] Préstamo creado: '{libro['titulo']}' → {usuario} ({fecha})")

    except sqlite3.Error as e:
        conexion.rollback()
        print(f"[ERROR] No se pudo crear el préstamo. Operación revertida: {e}")
    finally:
        cursor.close()
        conexion.close()


# ─────────────────────────────────────────────
# CRUD - LEER PRÉSTAMOS
# ─────────────────────────────────────────────

def leer_prestamos(usuario=None, libro_id=None, fecha_desde=None, fecha_hasta=None):
    """
    Muestra todos los préstamos registrados.
    Admite filtros opcionales por usuario, libro_id y rango de fechas.
    """
    conexion = conectar()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()

        query = "SELECT * FROM prestamos WHERE 1=1"
        params = []

        if usuario:
            query += " AND usuario = ?"
            params.append(usuario)
        if libro_id:
            query += " AND libro_id = ?"
            params.append(libro_id)
        if fecha_desde:
            query += " AND fecha_prestamo >= ?"
            params.append(fecha_desde)
        if fecha_hasta:
            query += " AND fecha_prestamo <= ?"
            params.append(fecha_hasta)

        cursor.execute(query, params)
        prestamos = cursor.fetchall()

        if not prestamos:
            print("[INFO] No se encontraron préstamos con los filtros indicados.")
            return

        # CORREGIDO: error de sintaxis en la línea 79
        print("\n" + "─" * 65)
        print(f"{'ID':<5} {'Libro ID':<10} {'Usuario':<20} {'Fecha Préstamo':<16} {'Devolución':<16} {'Estado'}")
        print("─" * 75)
        for p in prestamos:
            devolucion = p["fecha_devolucion"] if p["fecha_devolucion"] else "Pendiente"
            print(f"{p['id']:<5} {p['libro_id']:<10} {p['usuario']:<20} {p['fecha_prestamo']:<16} {devolucion:<16} {p['estado']}")
        print("─" * 75)

    except sqlite3.Error as e:
        print(f"[ERROR] No se pudieron leer los préstamos: {e}")
    finally:
        cursor.close()
        conexion.close()


# ─────────────────────────────────────────────
# CRUD - ACTUALIZAR PRÉSTAMO (DEVOLUCIÓN)
# ─────────────────────────────────────────────

def devolver_libro(prestamo_id, fecha_devolucion):
    """
    Registra la devolución de un préstamo.
    Actualiza la fecha de devolución, el estado del préstamo y
    restaura la disponibilidad del libro a 1 (disponible).
    """
    conexion = conectar()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()

        # Obtener el préstamo
        cursor.execute("SELECT * FROM prestamos WHERE id = ?", (prestamo_id,))
        prestamo = cursor.fetchone()

        if prestamo is None:
            print(f"[ERROR] No existe ningún préstamo con id {prestamo_id}.")
            return

        if prestamo["estado"] == "devuelto":
            print(f"[INFO] El préstamo {prestamo_id} ya fue devuelto.")
            return

        libro_id = prestamo["libro_id"]

        # Actualizar fecha de devolución y estado del préstamo
        cursor.execute(
            "UPDATE prestamos SET fecha_devolucion = ?, estado = 'devuelto' WHERE id = ?",
            (fecha_devolucion, prestamo_id)
        )

        # Restaurar disponibilidad del libro
        cursor.execute("UPDATE libros SET disponible = 1 WHERE id = ?", (libro_id,))

        conexion.commit()
        print(f"[OK] Préstamo {prestamo_id} marcado como devuelto el {fecha_devolucion}. Libro {libro_id} disponible de nuevo.")

    except sqlite3.Error as e:
        conexion.rollback()
        print(f"[ERROR] No se pudo registrar la devolución. Operación revertida: {e}")
    finally:
        cursor.close()
        conexion.close()


# ─────────────────────────────────────────────
# CRUD - ELIMINAR PRÉSTAMO
# ─────────────────────────────────────────────

def eliminar_prestamo(prestamo_id):
    """
    Elimina un préstamo por su ID.
    Usa commit() si tiene éxito y rollback() si ocurre algún error.
    """
    conexion = conectar()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()

        # Comprobar que el préstamo existe
        cursor.execute("SELECT id FROM prestamos WHERE id = ?", (prestamo_id,))
        if cursor.fetchone() is None:
            print(f"[ERROR] No existe ningún préstamo con id {prestamo_id}.")
            return

        cursor.execute("DELETE FROM prestamos WHERE id = ?", (prestamo_id,))
        conexion.commit()
        print(f"[OK] Préstamo {prestamo_id} eliminado correctamente.")

    except sqlite3.Error as e:
        conexion.rollback()
        print(f"[ERROR] No se pudo eliminar el préstamo. Operación revertida: {e}")
    finally:
        cursor.close()
        conexion.close()


# ─────────────────────────────────────────────
# JOIN - PRÉSTAMOS CON DATOS DEL LIBRO
# ─────────────────────────────────────────────

def prestamos_con_libros():
    """
    Consulta con JOIN entre préstamos y libros.
    Muestra el id del préstamo, usuario, título del libro,
    fecha de préstamo y fecha de devolución.
    """
    conexion = conectar()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                p.id            AS id_prestamo,
                p.usuario,
                l.titulo        AS titulo_libro,
                p.fecha_prestamo,
                p.fecha_devolucion,
                p.estado
            FROM prestamos p
            JOIN libros l ON p.libro_id = l.id
            ORDER BY p.id
        """)

        resultados = cursor.fetchall()

        if not resultados:
            print("[INFO] No hay préstamos registrados.")
            return

        print("\n" + "─" * 85)
        print(f"{'ID':<5} {'Usuario':<20} {'Título':<25} {'Préstamo':<14} {'Devolución':<14} {'Estado'}")
        print("─" * 85)
        for r in resultados:
            devolucion = r["fecha_devolucion"] if r["fecha_devolucion"] else "Pendiente"
            print(f"{r['id_prestamo']:<5} {r['usuario']:<20} {r['titulo_libro']:<25} {r['fecha_prestamo']:<14} {devolucion:<14} {r['estado']}")
        print("─" * 85)

    except sqlite3.Error as e:
        print(f"[ERROR] No se pudo ejecutar la consulta JOIN: {e}")
    finally:
        cursor.close()
        conexion.close()


# ─────────────────────────────────────────────
# COUNT - TOTAL DE PRÉSTAMOS POR LIBRO
# ─────────────────────────────────────────────

def total_prestamos_por_libro():
    """
    Consulta con LEFT JOIN, COUNT y GROUP BY.
    Muestra el número total de préstamos registrados para cada libro,
    incluyendo los libros que nunca han sido prestados (COUNT = 0).
    """
    conexion = conectar()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                l.id            AS id_libro,
                l.titulo,
                COUNT(p.id)     AS total_prestamos
            FROM libros l
            LEFT JOIN prestamos p ON l.id = p.libro_id
            GROUP BY l.id, l.titulo
            ORDER BY total_prestamos DESC
        """)

        resultados = cursor.fetchall()

        if not resultados:
            print("[INFO] No hay libros registrados.")
            return

        print("\n" + "─" * 50)
        print(f"{'ID':<6} {'Título':<30} {'Préstamos'}")
        print("─" * 50)
        for r in resultados:
            print(f"{r['id_libro']:<6} {r['titulo']:<30} {r['total_prestamos']}")
        print("─" * 50)

    except sqlite3.Error as e:
        print(f"[ERROR] No se pudo ejecutar la consulta de agregación: {e}")
    finally:
        cursor.close()
        conexion.close()
       
