from db import execute

def listar_deportes_db():
    query = "SELECT id, nombre FROM deportes ORDER BY id ASC;"
    return execute(query)