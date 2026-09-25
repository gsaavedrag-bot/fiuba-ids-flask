import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'club_deportivo')
}


def get_connection():
    """Abre una conexión MySQL usando la configuración centralizada."""
    return mysql.connector.connect(**db_config)


def execute(query: str, params: tuple = None):
    """
    Ejecuta SQL parametrizado y devuelve el resultado según el tipo de consulta:
    SELECT devuelve filas como diccionarios; INSERT devuelve el ID generado;
    otras instrucciones confirman los cambios y devuelven las filas afectadas.
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
