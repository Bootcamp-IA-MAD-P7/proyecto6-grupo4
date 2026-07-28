# T-5.3 — Esquema de persistencia (PostgreSQL)

## Motor y configuración

- Motor: **PostgreSQL**, vía SQLAlchemy 2.0 + driver `psycopg` (v3).
- Configuración: variable de entorno `DATABASE_URL`.
  - Local/dev por defecto (documentado, no hardcodeado): `postgresql+psycopg://laliga:laliga@localhost:5432/laliga`.
  - Si `DATABASE_URL` no está definida, `src/persistence/db.py` usa SQLite en memoria — solo para que los tests unitarios corran sin infraestructura. **En producción/desarrollo real siempre debe apuntar a Postgres.**
- El esquema se crea de forma idempotente al arrancar el backend (`init_schema()` en el evento `startup` de FastAPI) — no requiere una migración manual para el estado actual del proyecto. Si el esquema evoluciona de forma incompatible en el futuro, esto debería reemplazarse por una herramienta de migraciones (Alembic), no está en el alcance de T-5.3.
- La persistencia es **best-effort**: si la base de datos no está disponible, `/api/v1/predictions` y `/api/v1/feedback` siguen respondiendo con el contrato normal (el feedback además sigue su ruta ya validada de T-4.3 hacia el CSV recuperable). El fallo de persistencia se registra en el log del backend, nunca rompe la respuesta al cliente.

## Tabla `predictions`

Una fila por cada predicción servida por `POST /api/v1/predictions`.

| Columna | Tipo | Notas |
|---|---|---|
| `id` | `varchar(36)` (PK) | UUID generado al persistir. |
| `request_id` | `varchar(36)` | Mismo `request_id` devuelto en la respuesta de la API; indexado. |
| `home_team` | `varchar(80)` | |
| `away_team` | `varchar(80)` | |
| `match_date` | `date` | |
| `prediction` | `varchar(1)` | `H`, `D` o `A`. |
| `probability_h` / `probability_d` / `probability_a` | `float` | Suman 1.0 (validado en el contrato de la API, no a nivel de esquema). |
| `model_version` | `varchar(120)` | Versión del Champion que sirvió la predicción. |
| `data_version` | `varchar(120)` | SHA-256 del dataset usado por ese Champion. |
| `latency_ms` | `float` | Latencia medida igual que en la respuesta de la API. |
| `created_at` | `timestamptz` | Generado en el servidor. |

## Tabla `feedback`

Una fila por cada feedback recibido en `POST /api/v1/feedback`. Mismo
contrato de campos que `src/feedback/store.py` (T-4.3); esta tabla es la
persistencia durable, el CSV append-only de T-4.3 se mantiene sin cambios
como mecanismo adicional sin infraestructura.

| Columna | Tipo | Notas |
|---|---|---|
| `id` | `varchar(36)` (PK) | UUID interno de la fila. |
| `feedback_id` | `varchar(36)` | Igual al `feedback_id` devuelto por la API y al de la fila CSV correspondiente; único, indexado. |
| `home_team` / `away_team` | `varchar(80)` | |
| `match_date` | `date` | |
| `predicted_result` | `varchar(1)` nullable | `H`/`D`/`A` u omitido. |
| `actual_result` | `varchar(1)` | `H`, `D` o `A`; obligatorio. |
| `model_version` / `data_version` | `varchar(120)` nullable | |
| `comment` | `varchar(500)` nullable | |
| `received_at` | `timestamptz` | Generado en el servidor. |

## Verificación de persistencia tras reinicio

Verificado manualmente con un contenedor Docker real (`postgres:16`, volumen
nombrado `laliga_pg_data`):

1. Se levantó Postgres y se inicializó el esquema (`init_schema()`).
2. Se insertaron una predicción y un feedback de prueba vía `src/persistence/repository.py`.
3. Se reinició el contenedor (`docker restart`), simulando la caída y
   recuperación del servicio de base de datos independientemente del proceso
   de la API.
4. Se volvió a consultar la base de datos: **las filas seguían presentes**,
   confirmando persistencia real respaldada por el volumen de Docker, no por
   memoria del proceso.

## Reproducción local

```powershell
docker run -d --name laliga-postgres -e POSTGRES_USER=laliga -e POSTGRES_PASSWORD=laliga -e POSTGRES_DB=laliga -p 5432:5432 -v laliga_pg_data:/var/lib/postgresql/data postgres:16
$env:DATABASE_URL = "postgresql+psycopg://laliga:laliga@localhost:5432/laliga"
./.venv/Scripts/python.exe -c "from src.persistence.db import init_schema; init_schema()"
```
