# services/canchas_services.py
from db import execute


def contar_canchas_disponibles_db(inicio: str, fin: str, id_deporte: int | None = None, techada: bool | None = None) -> int:
    query = """
        SELECT COUNT(*) AS total
        FROM canchas c
        WHERE c.activa = TRUE
          AND c.id_cancha NOT IN (
              SELECT r.id_cancha
              FROM reservas r
              WHERE r.estado = 'confirmada'
                AND r.fecha_hora_inicio < %s
                AND r.fecha_hora_fin > %s
          )
    """
    params = [fin, inicio]
    if id_deporte is not None:
        query += " AND c.id_deporte = %s"
        params.append(id_deporte)
    if techada is not None:
        query += " AND c.techada = %s"
        params.append(techada)

    res = execute(query, tuple(params))
    return res[0]["total"] if res else 0


def obtener_canchas_disponibles_db(
    inicio: str,
    fin: str,
    id_deporte: int | None = None,
    techada: bool | None = None,
    limit: int = 10,
    offset: int = 0
) -> list[dict] | None:
    query = """
        SELECT c.id_cancha AS id, c.nombre, c.id_deporte, c.precio_hora, c.techada, c.activa
        FROM canchas c
        WHERE c.activa = TRUE
          AND c.id_cancha NOT IN (
              SELECT r.id_cancha
              FROM reservas r
              WHERE r.estado = 'confirmada'
                AND r.fecha_hora_inicio < %s
                AND r.fecha_hora_fin > %s
          )
    """
    params = [fin, inicio]
    if id_deporte is not None:
        query += " AND c.id_deporte = %s"
        params.append(id_deporte)
    if techada is not None:
        query += " AND c.techada = %s"
        params.append(techada)

    query += " ORDER BY c.id_cancha ASC LIMIT %s OFFSET %s;"
    params.extend([limit, offset])

    return execute(query, tuple(params))
