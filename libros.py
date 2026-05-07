from database import conectar

# ------------------------------------------------------------
# CREATE: Añadir un nuevo libro
# ------------------------------------------------------------
def crear_libro(titulo, autor, año):
    """Inserta un nuevo libro en la base de datos (disponible = 1 por defecto)."""
    conexion = conectar()
    if conexion is None:
        return False

    try:
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO libros (titulo, autor, año, disponible) VALUES (?, ?, ?, 1)",
            (titulo, autor, año)
        )
        conexion.commit()
        print(f" Libro '{titulo}' añadido correctamente.")
        return True
    except Exception as e:
        conexion.rollback()
        print(f" Error al añadir libro: {e}")
        return False
    finally:
        conexion.close()

# ------------------------------------------------------------
# READ: Leer libros con filtros y ordenación
# ------------------------------------------------------------
def leer_libros(filtro_autor=None, solo_disponibles=False, ordenar_por="año"):
    """
    Muestra los libros.
    - filtro_autor: texto para filtrar por autor (contiene)
    - solo_disponibles: True para mostrar solo disponibles (disponible = 1)
    - ordenar_por: "año", "titulo" o "autor"
    """
    conexion = conectar()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()
        query = "SELECT id, titulo, autor, año, disponible FROM libros WHERE 1=1"
        params = []

        if filtro_autor:
            query += " AND autor LIKE ?"
            params.append(f"%{filtro_autor}%")
        if solo_disponibles:
            query += " AND disponible = 1"

        if ordenar_por == "año":
            query += " ORDER BY año"
        elif ordenar_por == "titulo":
            query += " ORDER BY titulo"
        elif ordenar_por == "autor":
            query += " ORDER BY autor"
        else:
            query += " ORDER BY id"

        cursor.execute(query, params)
        libros = cursor.fetchall()

        if not libros:
            print("📭 No hay libros que coincidan con los filtros.")
            return

        print("\n" + "=" * 85)
        print(f"{'ID':<5} {'Título':<30} {'Autor':<25} {'Año':<6} {'Disponible'}")
        print("-" * 85)
        for l in libros:
            disp = "Sí" if l["disponible"] == 1 else "No"
            print(f"{l['id']:<5} {l['titulo']:<30} {l['autor']:<25} {l['año']:<6} {disp}")
        print("=" * 85 + "\n")

    except Exception as e:
        print(f" Error al leer libros: {e}")
    finally:
        conexion.close()

# ------------------------------------------------------------
# UPDATE: Actualizar un libro existente
# ------------------------------------------------------------
def actualizar_libro(id_libro, titulo=None, autor=None, año=None, disponible=None):
    """Actualiza los campos indicados de un libro."""
    conexion = conectar()
    if conexion is None:
        return False

    try:
        cursor = conexion.cursor()
        # Comprobar si el libro existe
        cursor.execute("SELECT id FROM libros WHERE id = ?", (id_libro,))
        if not cursor.fetchone():
            print(f" No existe un libro con id {id_libro}.")
            return False

        # Construir la actualización dinámica
        campos = []
        valores = []
        if titulo is not None:
            campos.append("titulo = ?")
            valores.append(titulo)
        if autor is not None:
            campos.append("autor = ?")
            valores.append(autor)
        if año is not None:
            campos.append("año = ?")
            valores.append(año)
        if disponible is not None:
            campos.append("disponible = ?")
            valores.append(disponible)

        if not campos:
            print(" No se proporcionó ningún campo para actualizar.")
            return False

        valores.append(id_libro)
        query = f"UPDATE libros SET {', '.join(campos)} WHERE id = ?"
        cursor.execute(query, valores)
        conexion.commit()
        print(f" Libro con id {id_libro} actualizado correctamente.")
        return True
    except Exception as e:
        conexion.rollback()
        print(f" Error al actualizar libro: {e}")
        return False
    finally:
        conexion.close()

# ------------------------------------------------------------
# DELETE: Eliminar un libro (solo si no tiene préstamos activos)
# ------------------------------------------------------------
def eliminar_libro(id_libro):
    """Elimina un libro solo si no tiene préstamos asociados (activos o devueltos)."""
    conexion = conectar()
    if conexion is None:
        return False

    try:
        cursor = conexion.cursor()
        # Verificar si tiene préstamos (cualquier estado)
        cursor.execute("SELECT COUNT(*) FROM prestamos WHERE libro_id = ?", (id_libro,))
        count = cursor.fetchone()[0]
        if count > 0:
            print(f" No se puede eliminar el libro porque tiene {count} préstamos asociados. Usa la transacción si quieres borrar todo.")
            return False

        cursor.execute("DELETE FROM libros WHERE id = ?", (id_libro,))
        if cursor.rowcount == 0:
            print(f" No existe un libro con id {id_libro}.")
            return False

        conexion.commit()
        print(f" Libro con id {id_libro} eliminado correctamente.")
        return True
    except Exception as e:
        conexion.rollback()
        print(f" Error al eliminar libro: {e}")
        return False
    finally:
        conexion.close()