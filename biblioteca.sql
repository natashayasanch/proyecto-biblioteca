-- Tabla de libros
CREATE TABLE IF NOT EXISTS libros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo VARCHAR(200) NOT NULL,
    autor VARCHAR(100) NOT NULL,
    año INTEGER NOT NULL,
    disponible INTEGER DEFAULT 1
);

-- Tabla de préstamos
CREATE TABLE IF NOT EXISTS prestamos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    libro_id INTEGER NOT NULL,
    usuario VARCHAR(100) NOT NULL,
    fecha_prestamo DATE NOT NULL,
    fecha_devolucion DATE NULL,
    estado VARCHAR(20) DEFAULT 'activo',
    FOREIGN KEY (libro_id) REFERENCES libros(id)
);

-- Índices para mejorar rapidez
CREATE INDEX idx_prestamos_libro_id ON prestamos(libro_id);
CREATE INDEX idx_prestamos_usuario ON prestamos(usuario);
CREATE INDEX idx_libros_autor ON libros(autor);
CREATE INDEX idx_libros_disponible ON libros(disponible);