import sqlite3

# ─────────────────────────────────────────────
# CONEXIÓN A LA BASE DE DATOS
# ─────────────────────────────────────────────
from database import conectar


# ─────────────────────────────────────────────
# OBTENER PRÉSTAMO POR ID (FUNCIÓN AUXILIAR)
# ─────────────────────────────────────────────
def obtener_prestamo_por_id(prestamo_id):
    """
    Busca un préstamo por su ID en la BD.
    Si no existe, devuelve None (bastante útil para validaciones).
    """
    conexion = conectar()
    if conexion is None:
        return None  # si no hay conexión, no seguimos

    try:
        cursor = conexion.cursor()

        # consulta simple por id
        cursor.execute("SELECT * FROM prestamos WHERE id = ?", (prestamo_id,))
        return cursor.fetchone()

    except sqlite3.Error as e:
        print(f"[ERROR] No se pudo obtener el préstamo: {e}")
        return None

    finally:
        # cierro todo siempre para evitar problemas de conexiones abiertas
        cursor.close()
        conexion.close()


# ─────────────────────────────────────────────
# CREAR PRÉSTAMO
# ─────────────────────────────────────────────
def crear_prestamo(libro_id, usuario, fecha):
    """
    Crea un préstamo nuevo.
    IMPORTANTE: antes comprueba que el libro exista y esté disponible.
    """
    conexion = conectar()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()

        # primero miro si el libro existe
        cursor.execute("SELECT id, titulo, disponible FROM libros WHERE id = ?", (libro_id,))
        libro = cursor.fetchone()

        if libro is None:
            print(f"[ERROR] No existe ningún libro con id {libro_id}.")
            return

        # si ya está prestado, no dejamos repetirlo
        if libro["disponible"] == 0:
            print(f"[ERROR] El libro '{libro['titulo']}' ya está prestado.")
            return

        # si todo está bien, creo el préstamo
        cursor.execute(
            "INSERT INTO prestamos (libro_id, usuario, fecha_prestamo, fecha_devolucion, estado) "
            "VALUES (?, ?, ?, NULL, 'activo')",
            (libro_id, usuario, fecha)
        )

        # y marco el libro como no disponible
        cursor.execute("UPDATE libros SET disponible = 0 WHERE id = ?", (libro_id,))

        conexion.commit()
        print(f"[OK] Préstamo creado: '{libro['titulo']}' → {usuario} ({fecha})")

    except sqlite3.Error as e:
        conexion.rollback()  # si algo falla, deshago todo
        print(f"[ERROR] No se pudo crear el préstamo: {e}")

    finally:
        cursor.close()
        conexion.close()


# ─────────────────────────────────────────────
# LEER PRÉSTAMOS (CON FILTROS)
# ─────────────────────────────────────────────
def leer_prestamos(usuario=None, libro_id=None, fecha_desde=None, fecha_hasta=None):
    """
    Muestra préstamos con filtros opcionales.
    Esto me sirve bastante para depurar o buscar cosas rápido.
    """
    conexion = conectar()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()

        query = "SELECT * FROM prestamos WHERE 1=1"
        params = []

        # voy añadiendo filtros según lo que me pasen
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
            print("[INFO] No se encontraron préstamos.")
            return

        # formato bonito en consola (aunque sea básico)
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
    Marca un préstamo como devuelto y vuelve a liberar el libro.
    """
    conexion = conectar()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()

        # busco el préstamo primero
        cursor.execute("SELECT * FROM prestamos WHERE id = ?", (prestamo_id,))
        prestamo = cursor.fetchone()

        if prestamo is None:
            print(f"[ERROR] No existe el préstamo {prestamo_id}.")
            return

        # si ya está devuelto, no hago nada
        if prestamo["estado"] == "devuelto":
            print(f"[INFO] Este préstamo ya estaba devuelto.")
            return

        libro_id = prestamo["libro_id"]

        # actualizo préstamo
        cursor.execute(
            "UPDATE prestamos SET fecha_devolucion = ?, estado = 'devuelto' WHERE id = ?",
            (fecha_devolucion, prestamo_id)
        )

        # y libero el libro otra vez
        cursor.execute("UPDATE libros SET disponible = 1 WHERE id = ?", (libro_id,))

        conexion.commit()
        print(f"[OK] Préstamo {prestamo_id} devuelto correctamente.")

    except sqlite3.Error as e:
        conexion.rollback()
        print(f"[ERROR] Fallo al registrar devolución: {e}")

    finally:
        cursor.close()
        conexion.close()


# ─────────────────────────────────────────────
# ELIMINAR PRÉSTAMO
# ─────────────────────────────────────────────
def eliminar_prestamo(prestamo_id):
    """
    Borra un préstamo por ID (cuidado con esto, es definitivo).
    """
    conexion = conectar()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()

        # compruebo si existe antes de borrar
        cursor.execute("SELECT id FROM prestamos WHERE id = ?", (prestamo_id,))
        if cursor.fetchone() is None:
            print(f"[ERROR] No existe el préstamo {prestamo_id}.")
            return

        cursor.execute("DELETE FROM prestamos WHERE id = ?", (prestamo_id,))
        conexion.commit()

        print(f"[OK] Préstamo {prestamo_id} eliminado.")

    except sqlite3.Error as e:
        conexion.rollback()
        print(f"[ERROR] No se pudo eliminar: {e}")

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
  # hago un JOIN para unir préstamos con su libro correspondiente
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
  # formato de salida en consola
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
       
