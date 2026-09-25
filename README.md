# fiuba-ids-flask

Trabajo práctico de Flask para la materia **"Introducción al Desarrollo de Software"** — FIUBA.

---

## ⚽ Sistema de Reservas - Club Deportivo Encuentro

API REST desarrollada en **Python** y **Flask** para centralizar y automatizar la gestión de canchas, socios y reservas del Club Deportivo Encuentro.

---

## 👥 Integrantes

| Nombre y Apellido | Padrón |
| Martin simajowich | 106935 |
| Gabriel Alexander Saavedra Gutierrez | 114419 |
| Federico Albarracín | 116268 |
| Nicole Gomez | 112221 |
| Vanessa Michuy | 115947 |
| Adriana Camila Rodriguez Caballero | 116394 |

---

## 🚀 Características Principales

* **Gestión de Recursos:** Administración y actualización de canchas (fútbol, tenis, pádel), deportes y socios del club.
* **Control de Disponibilidad:** Consulta de turnos libres en tiempo real y prevención estricta de solapamientos horarios tanto por cancha como por socio.
* **Ciclo de Vida de Reservas:** Registro de reservas en franjas horarias válidas, cálculo automático de importes en centavos, congelamiento de tarifa histórica y transiciones de estado (`confirmada`, `cancelada`, `finalizada`).
* **Paginación y Filtros:** Respuestas paginadas mediante estándares HATEOAS (`_limit`, `_offset`, `_links`) y filtros multicriterio combinados por `AND`.
* **Contrato y Persistencia:** Documentación formal bajo especificación OpenAPI 3.0 (`swagger.yaml`) y persistencia en base de datos relacional SQL.

---

## ⚙️ Instalación y Configuración

Ejecutar los siguientes comandos en el directorio raíz del proyecto:

### 1. Configurar variables de entorno
```bash
cp .env.example .env

python3 -m venv .venv
source .venv/bin/activate
pip install -r requeriments.txt

3. Crear esquema de base de datos
Observación: El archivo schema.sql está configurado para crear una base de datos por defecto llamada prode.
sudo mysql -u root -p < schema.sql
Ejecutar el servidor
sudo mysql -u root -p < schema.sql
4. Ejecutar el servidor
python3 app.py

python3 app.py
