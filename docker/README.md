# T-5.2 — Dockerización

## Artefacto del Champion

`docker/backend.Dockerfile` **no reentrena nada** durante el build. Descarga
`laliga_champion_v1.joblib` desde el release público
`model-ensemble-abcd-soft-voting-v1` y comprueba su SHA-256 antes de continuar.
El binario permanece fuera del historial Git, pero un clon limpio puede
construir una imagen reproducible.

La huella esperada también se conserva en
`reports/experiments/champion_artifact.sha256`.

## Levantar todo

```powershell
docker compose up --build
```

- Backend: `http://localhost:8000` (`/health`, `/api/v1/predictions`, `/api/v1/feedback`).
- Frontend: `http://localhost:5173`.
- Postgres: `localhost:5432` (usuario/clave/base `laliga`; ver `docker-compose.yml`).

El backend espera a que Postgres esté `healthy` (`depends_on` con
`healthcheck`) antes de arrancar. Si Postgres no está disponible, el backend
sigue funcionando igual (persistencia *best-effort*, ver
`docs/database_schema.md`); solo no persiste predicciones/feedback en la
base de datos.

## Verificación

```powershell
docker compose up --build -d
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/v1/predictions -H "Content-Type: application/json" -d '{"home_team":"Real Madrid","away_team":"Barcelona","match_date":"2026-10-25"}'
docker compose down
```

## Despliegue público en Render

`render.yaml` define un Blueprint con:

- un servicio web Docker que sirve FastAPI y el frontend estático desde el
  mismo dominio;
- una base PostgreSQL administrada;
- health check real en `/health`, que falla si el Champion no puede cargarse;
- región Frankfurt y despliegue manual para evitar cambios accidentales.

Después de fusionar la rama en `develop`, abrir:

```text
https://render.com/deploy?repo=https://github.com/Bootcamp-IA-MAD-P7/proyecto6-grupo4
```

Revisar los dos recursos y pulsar **Deploy Blueprint**. Cuando termine:

1. abrir la URL `https://<servicio>.onrender.com/`;
2. comprobar `https://<servicio>.onrender.com/health`;
3. realizar una predicción desde la interfaz;
4. confirmar en Render que el servicio y PostgreSQL están activos.

El plan gratuito es suficiente para una demo, pero el servicio puede tener
arranque en frío y la base PostgreSQL gratuita caduca a los 30 días.
