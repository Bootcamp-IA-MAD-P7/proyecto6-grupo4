# T-5.2: imagen de servicio del backend. Los artefactos del Champion
# (models/champion/, data/processed/*.csv) se generan con el pipeline ya
# documentado en el repo (scripts/run_laliga_preprocessing.py,
# scripts/run_historical_features.py, scripts/run_candidate_{a,b,c,d}.py,
# scripts/run_ensemble_abcd.py, scripts/select_champion.py) ANTES de
# construir esta imagen: no se re-entrenan en el build (sería un build de
# ~10 minutos por el SVC calibrado). Ver docker/README.md.
FROM python:3.13-slim

WORKDIR /app

COPY requirements-backend.txt .
RUN pip install --no-cache-dir -r requirements-backend.txt

COPY src ./src
COPY app/backend ./app/backend
COPY data/processed/laliga_matches_clean.csv ./data/processed/laliga_matches_clean.csv
COPY reports/experiments/champion_metadata.json ./reports/experiments/champion_metadata.json
COPY models/champion ./models/champion

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
