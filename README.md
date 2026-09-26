# fiuba-ids-flask

Trabajo práctico de backend para la materia **"Introducción al Desarrollo de Software"** — Facultad de Ingeniería de la Universidad de Buenos Aires (FIUBA).

---

## ⚽ Sistema de Reservas - Club Deportivo Encuentro

API REST desarrollada en **Python** y **Flask** para centralizar y automatizar la administración y reserva de turnos para canchas de fútbol, tenis y pádel, garantizando la consistencia temporal de las operaciones y la integridad de las tarifas.

---

## 👥 Integrantes

| Nombre y Apellido | Padrón |
| :--- | :--- |
| Martin Simajowich | 106935 |
| Gabriel Alexander Saavedra Gutierrez | 114419 |
| Federico Albarracín | 116268 |
| Nicole Gomez | 112221 |
| Vanessa Michuy | 115947 |
| Adriana Camila Rodriguez Caballero | 116394 |

---

## 🚀 Características Principales

* **Gestión de Recursos:** Administración integral de canchas, deportes y socios del club.
* **Control de Disponibilidad:** Consulta de turnos libres en tiempo real y prevención estricta de solapamientos horarios (tanto por cancha como por socio en turnos simultáneos).
* **Ciclo de Vida de Reservas:** Creación en estado `confirmada`, cálculo de importes, congelamiento de tarifa histórica y transiciones controladas a `cancelada` o `finalizada`.
* **Paginación y Estándares HATEOAS:** Respuestas paginadas con `_limit` y `_offset`, acompañadas por enlaces de navegación (`_first`, `_prev`, `_next`, `_last`) y filtros combinables por `AND`.
* **Contrato OpenAPI 3.0:** Respuestas serializadas en JSON y manejo estructurado de errores (`400`, `404`, `409`, `500`) según la especificación formal de `swagger.yaml`.

---

## 🛠️ Tecnologías y Requisitos Previos

* **Lenguaje:** Python 3.10 o superior (desarrollado sobre Python 3.12)
* **Framework:** Flask 3.x
* **Base de Datos:** MySQL 8.0+
* **Driver:** `mysql-connector-python`
* **Variables de Entorno:** `python-dotenv`

---

## 📁 Estructura del Proyecto

El backend implementa una arquitectura desacoplada por capas:

```text
fiuba-ids-flask/
├── app.py                 # Punto de entrada de la aplicación y registro de Blueprints
├── db.py                  # Conexión centralizada a MySQL y ejecutor de consultas
├── errors.py              # Respuestas estandarizadas de error según esquema Swagger
├── helpers.py             # Funciones utilitarias compartidas
├── init_db.sql            # Script de inicialización de tablas y precarga de deportes
├── swagger.yaml           # Contrato OpenAPI 3.0 de la API
├── requirements.txt       # Dependencias del proyecto
├── .env.example           # Plantilla de variables de entorno
├── routes/                # Capa de transporte HTTP (Blueprints y ruteo)
├── controllers/           # Validación de peticiones y respuestas HTTP
└── services/              # Lógica de negocio y consultas SQL parametrizadas
```
## ⚙️ Instalación y Puesta en Marcha

Ejecutar los siguientes pasos en la terminal desde el directorio raíz del proyecto:

## 1. Clonar el repositorio y configurar variables de entorno

Bash:

```text
cp .env.example .env
```

Editar el archivo .env local asignando las credenciales correspondientes a su servidor MySQL (este archivo no se versiona en Git).

## 2. Crear y activar el entorno virtual
En Linux / macOS:

Bash:

```text
python3 -m venv .venv
source .venv/bin/activate
```

## En Windows:

Bash

```text
python -m venv .venv
.venv\Scripts\activate
```

## 3. Instalar las dependencias
Bash

```text
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Inicializar la base de datos

Ejecutar el script SQL para crear la estructura relacional de club_deportivo e insertar los deportes precargados:

Bash

```text
mysql -u root -p < init_db.sql
```

## 5. Iniciar la API
Bash

```text
python3 app.py
```

El servidor quedará disponible por defecto en: http://localhost:5000 (o en el puerto definido en FLASK_PORT).

---

## 📋 Supuestos y Reglas de Negocio
Manejo Horario y Estándar Temporal:

Todas las fechas y horas se procesan bajo el estándar ISO 8601 con zona horaria oficial GMT-3 (YYYY-MM-DDTHH:MM:SS-03:00).

El club opera de 08:00 a 23:00. Los turnos se reservan en horas en punto (duración de 1 a 3 horas completas).

Tarifas y Moneda:

Todos los precios se gestionan y persisten como números enteros que representan centavos para evitar inconsistencias de redondeo en coma flotante.

La reserva congela la tarifa horaria vigente al momento de su creación. Modificaciones futuras en la cancha no alteran reservas existentes.

Políticas de Integridad y Estados:

No se permite eliminar físicamente una cancha que posea reservas históricas o activas (responde 409 Conflict). En su lugar, se realiza una baja lógica desactivándola.

La cancelación (cancelada) solo es válida antes de que comience el horario de inicio del turno.

La finalización (finalizada) únicamente puede aplicarse una vez transcurrido el horario de finalización.

---

## 🧪 Ejemplos de Solicitudes (cURL)
Listar deportes precargados:

Bash

```text
curl -X GET http://localhost:5000/deportes
```

## Crear un nuevo socio:

Bash

```text
curl -X POST http://localhost:5000/socios \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Carlos Tevez", "email": "carlos.tevez@club.com"}'
```

## Consultar reservas paginadas con filtros:

Bash:
```text
curl -X GET "http://localhost:5000/reservas?estado=confirmada&_limit=5&_offset=0"
```
