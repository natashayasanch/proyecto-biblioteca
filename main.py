import sys
from datetime import date, datetime

# IMPORTAR MÓDULOS DE TUS COMPAÑEROS
from conexion import probar_conexion, conectar
from crud_libros import crear_libro, leer_libros, actualizar_libro, eliminar_libro_con_prestamos
from crud_prestamos import (
    crear_prestamo, leer_prestamos, devolver_libro, 
    eliminar_prestamo, obtener_prestamo_por_id
)
from consultas import prestamos_con_libros, total_prestamos_por_libro


#  FUNCIONES DE AYUDA (VALIDACIONES) 

def obtener_opcion_valida(min_val, max_val):
    """
    Solicita al usuario un número entre min_val y max_val.
    Maneja entradas no numéricas y valores fuera de rango.
    EJEMPLO DE MANEJO DE EXCEPCIONES #1
    """
    while True:
        try:
            opcion = int(input(" Elige una opción: "))
            if min_val <= opcion <= max_val:
                return opcion
            else:
                print(f" Opción no válida. Elige un número entre {min_val} y {max_val}.")
        except ValueError:
            print(" Entrada no válida. Debes introducir un número.")


def obtener_fecha_valida(mensaje="Fecha (YYYY-MM-DD)"):
    """
    Solicita una fecha en formato ISO y valida el formato.
    EJEMPLO DE MANEJO DE EXCEPCIONES #2
    """
    while True:
        fecha_str = input(f"{mensaje}: ").strip()
        if not fecha_str:
            return date.today().isoformat()
        try:
            datetime.strptime(fecha_str, "%Y-%m-%d")
            return fecha_str
        except ValueError:
            print(" Formato de fecha no válido. Usa YYYY-MM-DD (ej: 2024-04-20)")


def obtener_entero_positivo(mensaje):
    """
    Solicita un número entero positivo.
    EJEMPLO DE MANEJO DE EXCEPCIONES #3
    """
    while True:
        try:
            valor = int(input(mensaje))
            if valor > 0:
                return valor
            else:
                print(" El número debe ser positivo.")
        except ValueError:
            print(" Debes introducir un número entero.")


def confirmar_accion(mensaje):
    """Pide confirmación al usuario (s/n) para operaciones peligrosas."""
    respuesta = input(f"{mensaje} (s/n): ").strip().lower()
    return respuesta == 's' or respuesta == 'si'


#  MENÚ PRINCIPAL 

def main():
    """Función principal que ejecuta el menú cíclico."""
    
    print("=" * 55)
    print(" SISTEMA DE GESTIÓN DE BIBLIOTECA")
    print("=" * 55)
    
    # MANEJO DE EXCEPCIÓN #4: Probar conexión al iniciar
    if not probar_conexion():
        sys.exit(1)
    
    # BUCLE CÍCLICO DEL MENÚ (REQUISITO OBLIGATORIO)
    while True:
        print("\n" + "-" * 50)
        print("MENÚ PRINCIPAL")
        print("-" * 50)
        print("1. Añadir nuevo libro")
        print("2.Ver libros (con filtros)")
        print("3.Actualizar un libro")
        print("4.Eliminar un libro (y sus préstamos)")
        print("5.Registrar nuevo préstamo")
        print("6.Ver historial de préstamos")
        print("7.Devolver un libro")
        print("8.Eliminar un registro de préstamo")
        print("9.Ver préstamos con detalle de libro (JOIN)")
        print("10.Estadísticas: libros más prestados (COUNT)")
        print("0.Salir")
        print("-" * 50)

        opcion = obtener_opcion_valida(0, 10)

        # OPCIÓN 1: Añadir libro (usa código de Persona 1) 
        if opcion == 1:
            print("\n--- NUEVO LIBRO ---")
            titulo = input("Título: ").strip()
            if not titulo:
                print(" El título es obligatorio.")
                continue
            autor = input("Autor: ").strip()
            if not autor:
                print(" El autor es obligatorio.")
                continue
            
            # Validación de año con manejo de excepciones
            anio = None
            while True:
                anio_str = input("Año de publicación (opcional): ").strip()
                if not anio_str:
                    break
                try:
                    anio = int(anio_str)
                    if 0 <= anio <= 2025:
                        break
                    else:
                        print(" Año no válido. Debe estar entre 0 y 2025.")
                except ValueError:
                    print(" Debes introducir un número entero.")
            
            crear_libro(titulo, autor, anio)  # ← Llama a función de P1

        #  OPCIÓN 2: Ver libros (usa código de Persona 1) 
        elif opcion == 2:
            print("\n--- CONSULTAR LIBROS ---")
            filtro_autor = input("Filtrar por autor (dejar vacío para ignorar): ").strip()
            filtro_autor = filtro_autor if filtro_autor else None
            
            solo_disponibles = input("¿Mostrar solo disponibles? (s/n): ").strip().lower() == 's'
            
            print("Ordenar por: (1) ID | (2) Título | (3) Año | (4) Autor")
            orden_opcion = input("Opción (default 1): ").strip()
            orden_map = {'1': 'id', '2': 'titulo', '3': 'anio', '4': 'autor'}
            ordenar_por = orden_map.get(orden_opcion, 'id')
            
            leer_libros(filtro_autor, solo_disponibles, ordenar_por)  # ← Llama a P1

        #  OPCIÓN 3: Actualizar libro (usa código de Persona 1) 
        elif opcion == 3:
            print("\n--- ACTUALIZAR LIBRO ---")
            id_libro = obtener_entero_positivo("ID del libro a actualizar: ")
            
            print("Deja en blanco los campos que NO quieras modificar.")
            nuevo_titulo = input("Nuevo título: ").strip()
            nuevo_titulo = nuevo_titulo if nuevo_titulo else None
            
            nuevo_autor = input("Nuevo autor: ").strip()
            nuevo_autor = nuevo_autor if nuevo_autor else None
            
            nuevo_anio_str = input("Nuevo año: ").strip()
            nuevo_anio = int(nuevo_anio_str) if nuevo_anio_str.isdigit() else None
            
            actualizar_libro(id_libro, nuevo_titulo, nuevo_autor, nuevo_anio)  # ← P1

        #  OPCIÓN 4: Eliminar libro con TRANSACCIÓN (usa código de Persona 1) 
        elif opcion == 4:
            print("\n--- ELIMINAR LIBRO ---")
            id_libro = obtener_entero_positivo("ID del libro a eliminar: ")
            
            if confirmar_accion(f" ¿Estás seguro de eliminar el libro ID {id_libro} y TODOS sus préstamos?"):
                eliminar_libro_con_prestamos(id_libro)  # ← TRANSACCIÓN de P1
            else:
                print("Operación cancelada.")

        #  OPCIÓN 5: Nuevo préstamo (usa código de Persona 2) 
        elif opcion == 5:
            print("\n--- NUEVO PRÉSTAMO ---")
            id_libro = obtener_entero_positivo("ID del libro a prestar: ")
            usuario = input("Nombre del usuario: ").strip()
            if not usuario:
                print(" El nombre del usuario es obligatorio.")
                continue
            fecha = obtener_fecha_valida("Fecha de préstamo")
            
            crear_prestamo(id_libro, usuario, fecha)  # ← Llama a función de P2

        #  OPCIÓN 6: Ver préstamos (usa código de Persona 2) 
        elif opcion == 6:
            print("\n--- HISTORIAL DE PRÉSTAMOS ---")
            print("Filtros (dejar vacío para ignorar):")
            usuario = input("Usuario: ").strip()
            usuario = usuario if usuario else None
            
            libro_id_str = input("ID del libro: ").strip()
            libro_id = int(libro_id_str) if libro_id_str.isdigit() else None
            
            fecha_desde = input("Fecha desde (YYYY-MM-DD): ").strip()
            fecha_desde = fecha_desde if fecha_desde else None
            fecha_hasta = input("Fecha hasta (YYYY-MM-DD): ").strip()
            fecha_hasta = fecha_hasta if fecha_hasta else None
            
            leer_prestamos(usuario, libro_id, fecha_desde, fecha_hasta)  # ← P2

        #  OPCIÓN 7: Devolver libro (usa código de Persona 2) 
        elif opcion == 7:
            print("\n--- DEVOLVER LIBRO ---")
            prestamo_id = obtener_entero_positivo("ID del préstamo a devolver: ")
            
            # Validación adicional: verificar que el préstamo existe
            prestamo = obtener_prestamo_por_id(prestamo_id)
            if not prestamo:
                print(f" No existe un préstamo con ID {prestamo_id}.")
                continue
            if prestamo['estado'] == 'devuelto':
                print(f" El préstamo {prestamo_id} ya fue devuelto.")
                continue
            
            fecha = obtener_fecha_valida("Fecha de devolución")
            devolver_libro(prestamo_id, fecha)  # ← P2

        # OPCIÓN 8: Eliminar préstamo (usa código de Persona 2) 
        elif opcion == 8:
            print("\n--- ELIMINAR PRÉSTAMO ---")
            prestamo_id = obtener_entero_positivo("ID del préstamo a eliminar: ")
            
            prestamo = obtener_prestamo_por_id(prestamo_id)
            if not prestamo:
                print(f" No existe un préstamo con ID {prestamo_id}.")
                continue
            
            if confirmar_accion(f" ¿Eliminar el préstamo {prestamo_id}? Esta acción es irreversible."):
                eliminar_prestamo(prestamo_id)  # ← P2

        #  OPCIÓN 9: JOIN (usa código de Persona 2) 
        elif opcion == 9:
            print("\n--- PRÉSTAMOS CON DETALLE DE LIBRO (JOIN) ---")
            prestamos_con_libros()  # ← CONSULTA JOIN de P2

        #  OPCIÓN 10: Agregación COUNT (usa código de Persona 2) 
        elif opcion == 10:
            print("\n--- ESTADÍSTICAS: PRÉSTAMOS POR LIBRO ---")
            total_prestamos_por_libro()  # ← CONSULTA AGREGACIÓN de P2

        #  OPCIÓN 0: Salir 
        elif opcion == 0:
            print("\n ¡Gracias por usar el sistema de biblioteca! ¡Hasta pronto!")
            break


#  PUNTO DE ENTRADA 
if __name__ == "__main__":
    main()