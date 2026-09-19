import os
import mysql.connector
from dotenv import load_dotenv

# Carga las variables desde el archivo .env local
load_dotenv()

def get_connection():
    """
    Retorna la conexión física a la base de datos MySQL
    usando las variables de entorno.
    """
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DATABASE', 'club_encuentro')
    )

def execute(query: str, params: tuple = None):
    """
    Ejecuta consultas SQL contra la base de datos:
    - SELECT: retorna una lista de diccionarios [{'columna': valor}, ...].
    - INSERT: retorna el ID generado (lastrowid).
    - UPDATE / DELETE: ejecuta el commit y retorna las filas afectadas (rowcount).
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        # dictionary=True mapea las columnas directo a claves JSON
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
        print(f"❌ Error en base de datos: {err}")
        return None

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()