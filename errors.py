from flask import jsonify


def build_error_response(code: int, message: str, description: str):
    """
    Construye la tupla (Response, HTTP_STATUS) respetando
    el schema 'Errores' exigido en swagger.yaml.
    """
    response = {
        "errors": [
            {
                "code": code,
                "message": message,
                "level": "error",
                "description": description
            }
        ]
    }
    return jsonify(response), code


# Mapeo uniforme para invocar directamente desde los controllers
ERRORS = {
    # 400 Bad Request
    "MISSING_REQUIRED_FIELDS": lambda msg="Faltan campos obligatorios": build_error_response(
        400, msg, "La solicitud no contiene todos los campos obligatorios."
    ),
    "INVALID_FORMAT": lambda msg="Formato de datos inválido": build_error_response(
        400, msg, "Los tipos o formatos de los datos proporcionados son incorrectos."
    ),

    # 404 Not Found
    "NOT_FOUND": lambda msg="Recurso no encontrado": build_error_response(
        404, msg, "El recurso solicitado no existe en la base de datos."
    ),

    # 409 Conflict (Emails repetidos, transiciones de estado inválidas, solapamientos)
    "CONFLICT": lambda msg="Conflicto de negocio": build_error_response(
        409, msg, "La operación no pudo completarse debido a un conflicto de estado o registros existentes."
    ),

    # 500 Internal Server Error
    "INTERNAL_SERVER_ERROR": lambda msg="Error interno en el servidor": build_error_response(
        500, msg, "Ocurrió un error inesperado al procesar la solicitud."
    )
}
