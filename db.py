import os
import mysql.connector
from dotenv import load_dotenv

# Carga de variables de entorno desde el .env
load_dotenv()

# Diccionario centralizado de configuración de conexión
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'club_deportivo')
}


def get_connection():
    """Establece la conexión usando desempaquetado de diccionario (kwargs)."""
    return mysql.connector.connect(**db_config)


def execute(query: str, params: tuple = None):
    """
    Ejecuta sentencias SQL de forma segura y maneja el ciclo de vida de la conexión:
    - SELECT: retorna lista de diccionarios (cursor.fetchall()).
    - INSERT: aplica commit y retorna el ID autogenerado (cursor.lastrowid).
    - UPDATE / DELETE: aplica commit y retorna las filas afectadas (cursor.rowcount).
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())

        instruccion = query.strip().upper()
        if instruccion.startswith("SELECT"):
            result = cursor.fetchall()
        elif instruccion.startswith("INSERT"):
            conn.commit()
            result = cursor.lastrowid
        else:
            conn.commit()
            result = cursor.rowcount

        return result

    except mysql.connector.Error as err:
        print(f"Error de base de datos: {err}")
        return None

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
