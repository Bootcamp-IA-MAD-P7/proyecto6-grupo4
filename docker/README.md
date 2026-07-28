# T-5.2 — Dockerización

## Prerrequisito: generar los artefactos del Champion

`docker/backend.Dockerfile` **no re-entrena nada** durante el build (el SVC
calibrado por sí solo tarda minutos; el pipeline completo, más aún). Copia
artefactos ya generados. Antes de construir la imagen, en el host:

```powershell
./.venv/Scripts/python.exe scripts/run_laliga_preprocessing.py
./.venv/Scripts/python.exe scripts/run_historical_features.py
./.venv/Scripts/python.exe scripts/run_candidate_a.py
./.venv/Scripts/python.exe scripts/run_candidate_b.py
./.venv/Scripts/python.exe scripts/run_candidate_c.py
./.venv/Scripts/python.exe scripts/run_candidate_d.py
./.venv/Scripts/python.exe scripts/run_ensemble_abcd.py
./.venv/Scripts/python.exe scripts/select_champion.py
```

Esto deja `models/champion/laliga_champion_v1.joblib`,
`reports/experiments/champion_metadata.json` y
`data/processed/laliga_matches_clean.csv` listos — exactamente los tres
artefactos que `docker/backend.Dockerfile` copia a la imagen.

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
