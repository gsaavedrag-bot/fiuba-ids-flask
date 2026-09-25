from db import execute

def listar_deportes_db():
    """Consulta los deportes y adapta el nombre de la clave para la API."""
    query = """
        SELECT 
            -- El esquema usa id_deporte; la respuesta pública usa id.
            id_deporte AS id,
            nombre
        FROM deportes
        -- ASC es el orden predeterminado: primero el menor identificador.
        ORDER BY id_deporte ASC;
    """
    # execute devuelve una lista de filas como diccionarios.
    return execute(query)