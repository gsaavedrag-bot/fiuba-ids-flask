import os
import mysql.connector
from dotenv import load_dotenv

# Cargamos las variables definidas en el archivo .env
load_dotenv()

def get_connection():
    """
    Establece y retorna la conexión física con el motor MySQL
    utilizando las credenciales del entorno.
    """
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'club_encuentro')
    )

def execute(query, params=None):
    """
    Función comodín que usarán todos en la capa 'services':
    - Si la consulta es SELECT: retorna una lista de diccionarios [ {campo: valor}, ... ].
    - Si es INSERT, UPDATE o DELETE: aplica el commit y retorna la cantidad de filas afectadas.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        # dictionary=True hace que los registros vuelvan como diccionarios {'id': 1, 'nombre': 'Tenis'}
        # en lugar de tuplas crudas (1, 'Tenis')
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())

        # Verificamos qué tipo de operación SQL es
        if query.strip().upper().startswith("SELECT"):
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.rowcount  # o cursor.lastrowid si necesitan el ID generado

        return result

    except mysql.connector.Error as err:
        print(f"❌ Error en base de datos: {err}")
        return False

    finally:
        # Siempre cerramos cursor y conexión para no saturar MySQL
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()