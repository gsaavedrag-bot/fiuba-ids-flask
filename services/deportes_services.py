from db import execute

def listar_deportes_db():
    query = """
        SELECT 
            id_deporte AS id,
            nombre
        FROM deportes
        ORDER BY id_deporte;
    """
    return execute(query)