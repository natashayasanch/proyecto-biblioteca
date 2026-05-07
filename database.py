import sqlite3

def conectar():
    conexion = sqlite3.connect("biblioteca.db")
    conexion.row_factory = sqlite3.Row
    _crear_tablas(conexion)
    return conexion

def _crear_tablas(conn):
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS libros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo VARCHAR(200) NOT NULL,
            autor VARCHAR(100) NOT NULL,
            año INTEGER NOT NULL,
            disponible INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS prestamos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            libro_id INTEGER NOT NULL,
            usuario VARCHAR(100) NOT NULL,
            fecha_prestamo DATE NOT NULL,
            fecha_devolucion DATE NULL,
            estado VARCHAR(20) DEFAULT 'activo',
            FOREIGN KEY (libro_id) REFERENCES libros(id)
        );

        CREATE INDEX IF NOT EXISTS idx_prestamos_libro_id ON prestamos(libro_id);
        CREATE INDEX IF NOT EXISTS idx_prestamos_usuario ON prestamos(usuario);
        CREATE INDEX IF NOT EXISTS idx_libros_autor ON libros(autor);
        CREATE INDEX IF NOT EXISTS idx_libros_disponible ON libros(disponible);
    """)
    conn.commit()