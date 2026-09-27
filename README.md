# ⚽ Sistema de Reservas - Club Deportivo Encuentro

Trabajo práctico de backend para la materia **"Introducción al Desarrollo de Software"** — Facultad de Ingeniería de la Universidad de Buenos Aires (FIUBA).

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

---

## ⚙️ Instalación y Puesta en Marcha

Sigue estos pasos en la terminal desde el directorio raíz del proyecto para levantar la aplicación:

### 1. Configurar Variables de Entorno

Clona la plantilla de variables de entorno y edítala con tus credenciales locales de MySQL:

```bash
cp .env.example .env
```

> **Nota:** No olvides asignar las credenciales correspondientes a tu servidor local de MySQL en el archivo `.env` recién creado. Este archivo está excluido del control de versiones.

### 2. Crear y Activar el Entorno Virtual

- **Linux / macOS:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

- **Windows (CMD o PowerShell):**
  ```cmd
  python -m venv .venv
  .venv\Scripts\activate
  ```

### 3. Instalar Dependencias

Actualiza `pip` e instala los paquetes requeridos:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Inicializar la Base de Datos

Ejecuta el script SQL para crear la base de datos `club_deportivo`, estructurar las tablas e insertar los deportes precargados:

```bash
mysql -u root -p < init_db.sql
```

### 5. Iniciar la API

Corre el servidor de Flask:

```bash
python3 app.py
```

El servidor quedará disponible por defecto en: [http://localhost:5000](http://localhost:5000) (o en el puerto definido por `FLASK_PORT` en tu `.env`).

---

## 📋 Supuestos y Reglas de Negocio

### 🕒 Manejo Horario y Estándar Temporal
* **Estándar:** Todas las fechas y horas se procesan bajo el estándar **ISO 8601** con zona horaria oficial GMT-3 (`YYYY-MM-DDTHH:MM:SS-03:00`).
* **Operación:** El club opera únicamente de **08:00 a 23:00**.
* **Turnos:** Los turnos se reservan en horas en punto con una duración de **1 a 3 horas completas**.

### 💵 Tarifas y Moneda
* **Consistencia:** Todos los precios se gestionan y persisten como **números enteros en centavos** para evitar inconsistencias de redondeo con coma flotante.
* **Congelamiento de Tarifa:** La reserva congela la tarifa horaria vigente al momento de su creación. Modificaciones futuras en la tarifa de la cancha no alterarán las reservas preexistentes.

### 🔒 Políticas de Integridad y Estados
* **Baja Lógica de Canchas:** No se permite eliminar físicamente una cancha que posea reservas históricas o activas (retorna `409 Conflict`). En su lugar, se realiza una baja lógica desactivándola.
* **Cancelaciones:** La cancelación (`cancelada`) solo es válida antes del horario de inicio del turno.
* **Finalización:** El cambio de estado a `finalizada` únicamente puede aplicarse una vez transcurrido el horario de finalización del turno.

---

## 🧪 Ejemplos de Solicitudes (cURL)

### Listar deportes precargados
```bash
curl -X GET http://localhost:5000/deportes
```

### Crear un nuevo socio
```bash
curl -X POST http://localhost:5000/socios \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Carlos Tevez", "email": "carlos.tevez@club.com"}'
```

### Consultar reservas paginadas con filtros
```bash
curl -X GET "http://localhost:5000/reservas?estado=confirmada&_limit=5&_offset=0"
```
