# T-5.4: imagen desplegable del backend y frontend. El Champion se descarga
# desde un release público versionado y se verifica antes de copiar el código.
FROM python:3.13-slim

WORKDIR /app

COPY requirements-backend.txt .
RUN pip install --no-cache-dir -r requirements-backend.txt

ARG CHAMPION_MODEL_URL=https://github.com/Bootcamp-IA-MAD-P7/proyecto6-grupo4/releases/download/model-ensemble-abcd-soft-voting-v1-f9c0e933/laliga_champion_v1.joblib
ARG CHAMPION_MODEL_SHA256=f9c0e93317924613e9dc8fb57125ecd5b227fdb0afa6fc7ec1f6e963407d5696
RUN mkdir -p models/champion && \
    python -c "from hashlib import sha256; from pathlib import Path; from urllib.request import urlretrieve; target=Path('models/champion/laliga_champion_v1.joblib'); urlretrieve('${CHAMPION_MODEL_URL}', target); actual=sha256(target.read_bytes()).hexdigest(); assert actual == '${CHAMPION_MODEL_SHA256}', f'SHA-256 inesperado: {actual}'"

COPY src ./src
COPY app/backend ./app/backend
COPY app/frontend-react/dist ./app/frontend-react/dist
COPY data/processed/laliga_matches_clean.csv ./data/processed/laliga_matches_clean.csv
COPY data/fixtures ./data/fixtures
COPY reports/experiments/champion_metadata.json ./reports/experiments/champion_metadata.json

EXPOSE 10000
CMD ["sh", "-c", "python -m uvicorn app.backend.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
