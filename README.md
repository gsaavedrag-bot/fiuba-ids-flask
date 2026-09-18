# fiuba-ids-flask
Trabajo practico de Flask para la materia "Introduccion al Desarrollo de Software" de la FIUBA.

FIXTURE SISTEMA DE RESERVA DE CLUB DEPORTIVO

Integrantes

Gabriel Alexander Saavedra Gutierrez 114419
Federico Albarraccín 116268
Nicole Gomez 112221
Nombre Apellidos Padron
Nombre Apellidos Padron
Nombre Apellidos Padron

# Sistema de Reservas - Club Deportivo Encuentro

API REST desarrollada en **Python** y **Flask** para centralizar y automatizar la gestión de canchas, socios y reservas del Club Deportivo Encuentro.

### Características Principales
* **Gestión de Recursos:** Administración y actualización de canchas (fútbol, tenis, pádel), deportes y socios del club.
* **Control de Disponibilidad:** Consulta de turnos libres en tiempo real y prevención estricta de solapamientos horarios tanto por cancha como por socio.
* **Ciclo de Vida de Reservas:** Registro de reservas en franjas horarias válidas, cálculo automático de importes en centavos, congelamiento de tarifa histórica y transiciones de estado (`confirmada`, `cancelada`, `finalizada`).
* **Paginación y Filtros:** Respuestas paginadas mediante estándares HATEOAS (`_limit`, `_offset`, `_links`) y filtros multicriterio combinados por `AND`.
* **Contrato y Persistencia:** Documentación formal bajo especificación OpenAPI 3.0 (`swagger.yaml`) y persistencia en base de datos relacional SQL.


Instalación

En el directorio del proyecto:
Configurar variables de entorno

cp .env.example .env

    Editar el archivo .env con las credenciales de la base de datos

Crear un entorno virtual e instalar las dependencias

python3 -m venv .venv
. .venv/bin/activate
pip install -r requeriments.txt

Crear esquema de base de datos

Observacion: El schema.sql esta configurado para crear una base de datos por defecto llamada "prode"

sudo mysql -u root -p < schema.sql
Ejecutar el servidor

python3 app.py
