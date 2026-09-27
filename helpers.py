# helpers.py
import re
from datetime import datetime, timezone, timedelta
from typing import Any

# Zona horaria oficial del club (GMT-3)
TZ_ARG = timezone(timedelta(hours=-3))

# Expresión regular estándar para correos
EMAIL_REGEX = re.compile(r"^[\w.-]+@[\w.-]+\.\w+$")


# ----------------------------------------------------------------------
# 1. Paginación y HATEOAS
# ----------------------------------------------------------------------

def parsear_paginacion(
    limit_raw: Any = 10,
    offset_raw: Any = 0,
    limit_default: int = 10,
    offset_default: int = 0
) -> tuple[int, int]:
    """
    Parsea y valida los parámetros de paginación.
    Lanza ValueError si no son enteros o están fuera de los límites permitidos:
      - _limit: entero entre 1 y 100.
      - _offset: entero mayor o igual a cero.
    """
    try:
        limit = int(limit_default if limit_raw is None else limit_raw)
        offset = int(offset_default if offset_raw is None else offset_raw)
    except (ValueError, TypeError):
        raise ValueError("Parámetros _limit y _offset deben ser números enteros.")

    if limit < 1 or limit > 100 or offset < 0:
        raise ValueError("Parámetros _limit (1-100) u _offset (>=0) inválidos.")

    return limit, offset


def build_hateoas_links(
    base_url: str,
    limit: int,
    offset: int,
    total: int,
    query_params: dict[str, Any]
) -> dict[str, dict[str, str]]:
    """
    Genera la navegación HATEOAS (_first, _prev, _next, _last)
    conservando los filtros de consulta enviados por el cliente.
    """
    # Excluir _limit y _offset previos para no duplicarlos en la query string
    filtros_limpios = {
        k: v for k, v in query_params.items() if k not in ("_limit", "_offset")
    }

    def generar_url(off: int) -> str:
        params = filtros_limpios | {"_offset": off, "_limit": limit}
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{base_url}?{qs}" if qs else f"{base_url}?_offset={off}&_limit={limit}"

    last_offset = max(0, ((total - 1) // limit) * limit) if total > 0 else 0
    prev_offset = max(0, offset - limit) if offset > 0 else None
    next_offset = offset + limit if (offset + limit) < total else None

    links = {
        "_first": {"href": generar_url(0)},
        "_last": {"href": generar_url(last_offset)}
    }
    if prev_offset is not None and offset > 0:
        links["_prev"] = {"href": generar_url(prev_offset)}
    if next_offset is not None:
        links["_next"] = {"href": generar_url(next_offset)}

    return links


# ----------------------------------------------------------------------
# 2. Conversión de booleanos
# ----------------------------------------------------------------------

def parsear_booleano(valor: Any, nombre_campo: str = "campo") -> bool | None:
    """
    Convierte parámetros de texto 'true', 'false', '1', '0' a bool nativo.
    Lanza ValueError si el valor no representa un booleano válido.
    """
    if valor is None:
        return None
    if isinstance(valor, bool):
        return valor

    val_str = str(valor).strip().lower()
    if val_str in ("true", "1"):
        return True
    if val_str in ("false", "0"):
        return False

    raise ValueError(f"El campo '{nombre_campo}' debe ser un booleano (true o false).")


# ----------------------------------------------------------------------
# 3. Formateo y validación de fechas / rango de reservas
# ----------------------------------------------------------------------

def parsear_fecha_iso(dt_value: datetime | str | None) -> str | None:
    """
    Formatea una fecha como ISO 8601 con 6 microsegundos y zona horaria GMT-3:
    Ejemplo: '2026-10-15T18:00:00.000000-03:00'
    """
    if dt_value is None:
        return None
    if isinstance(dt_value, str):
        dt_value = datetime.fromisoformat(dt_value)
    if dt_value.tzinfo is None:
        dt_value = dt_value.replace(tzinfo=TZ_ARG)
    return dt_value.strftime("%Y-%m-%dT%H:%M:%S.%f-03:00")


def validar_intervalo_reserva(inicio_iso: str, fin_iso: str) -> tuple[datetime, datetime]:
    """
    Comprueba las reglas temporales exigidas para las reservas:
      - Formato ISO 8601 correcto.
      - Inicio en el futuro respecto al momento actual.
      - Inicio menor a fin.
      - Minutos en 00 (horas en punto).
      - Duración entre 1 y 3 horas completas.
      - Rango dentro del horario de atención del club (08:00 a 23:00).
    Retorna la tupla (datetime_inicio, datetime_fin) con tzinfo GMT-3.
    """
    try:
        inicio = datetime.fromisoformat(inicio_iso)
        fin = datetime.fromisoformat(fin_iso)
    except (ValueError, TypeError):
        raise ValueError("Las fechas deben respetar el formato ISO 8601 con zona horaria.")

    if inicio.tzinfo is None:
        inicio = inicio.replace(tzinfo=TZ_ARG)
    if fin.tzinfo is None:
        fin = fin.replace(tzinfo=TZ_ARG)

    ahora = datetime.now(TZ_ARG)
    if inicio <= ahora:
        raise ValueError("La reserva debe comenzar en el futuro.")

    if inicio >= fin:
        raise ValueError("La fecha y hora de inicio debe ser anterior a la de fin.")

    duracion_horas = (fin - inicio).total_seconds() / 3600
    if duracion_horas < 1 or duracion_horas > 3 or not duracion_horas.is_integer():
        raise ValueError("La duración debe ser de entre 1 y 3 horas completas.")

    if inicio.hour < 8 or fin.hour > 23 or (fin.hour == 23 and fin.minute > 0):
        raise ValueError("El horario solicitado debe encontrarse entre las 08:00 y las 23:00.")

    if inicio.minute != 0 or inicio.second != 0 or fin.minute != 0 or fin.second != 0:
        raise ValueError("Las reservas deben iniciar y finalizar en horas en punto (HH:00:00).")

    return inicio, fin


def es_email_valido(email: Any) -> bool:
    """Indica si la sintaxis del correo electrónico es válida."""
    if not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))