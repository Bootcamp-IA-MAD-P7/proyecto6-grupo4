# Adquisición local de datos de LaLiga

## Política

Los datos se descargan para ejecutar localmente el proyecto de predicción de partidos. La revisión de T-0.2b no encontró una licencia abierta ni un permiso explícito para redistribuir los CSV raw o sus derivados fila a fila. Por ello:

- no se añadirán nuevos datasets a Git;
- los archivos de `data/raw/` y `data/processed/` se mantendrán locales;
- sí se versionarán código, schemas, diccionarios, manifests, huellas y métricas agregadas;
- cualquier publicación de los datos requerirá permiso escrito de la fuente.

Esta política es una decisión conservadora del proyecto y no constituye asesoramiento jurídico.

## Fuentes verificadas el 23/07/2026

### Histórico consolidado

- Archivo local esperado: `data/raw/LaLiga_Matches.csv`.
- Ficha: https://www.kaggle.com/datasets/kishan305/la-liga-results-19952020
- Publicador: Kishan Kumar.
- Origen declarado: Football-Data.co.uk.
- Declaración de licencia en Kaggle: `Data files © Original Authors`.
- SHA-256 de la instantánea usada por el proyecto: `d5d36d0ffff6dc73697e5bf794e19f0546fde07a77fe8caaf20eee60ca6ef2a7`.

La descarga se realiza manualmente desde la ficha de Kaggle con una cuenta autorizada. La etiqueta de Kaggle no concede una licencia abierta de redistribución.

### Temporada detallada 2025-2026

- Archivo local esperado: `data/raw/laliga_2025_2026_stats.csv`.
- Página oficial: https://www.football-data.co.uk/data.php
- Descarga publicada: https://www.football-data.co.uk/mmz4281/2526/SP1.csv
- Notas de columnas: https://www.football-data.co.uk/notes.txt
- SHA-256 de la instantánea usada por el proyecto: `22f754836d287254c9b4fc85001192a235f468a56bde5df540018914fc26dea4`.

Football-Data publica los datos gratuitamente y declara como finalidad la predicción de partidos de liga. No se encontró una licencia abierta ni una autorización explícita para republicar el archivo. La fuente es mutable; una descarga posterior puede no coincidir byte a byte con la instantánea usada.

## Preparación local

1. Crear `data/raw/` si no existe.
2. Descargar el histórico desde Kaggle y guardarlo como `data/raw/LaLiga_Matches.csv`.
3. Descargar `SP1.csv` desde Football-Data y guardarlo como `data/raw/laliga_2025_2026_stats.csv`.
4. Comparar las huellas con `reports/metrics/dataset_manifest.json`.
5. Si una huella difiere, no sustituir silenciosamente la versión canónica: registrar la nueva versión y volver a aprobar datos, splits y resultados.
6. Regenerar los artefactos:

```powershell
.\.venv\Scripts\python.exe scripts\run_laliga_preprocessing.py
.\.venv\Scripts\python.exe scripts\run_laliga_eda.py
.\.venv\Scripts\python.exe -m src.evaluation.splits
.\.venv\Scripts\python.exe -m pytest -q
```

## Reproducción exacta

Las páginas de origen pueden actualizar sus archivos. Para reproducir exactamente las huellas anteriores sin redistribuir públicamente, el equipo deberá conservar las instantáneas en almacenamiento privado con control de acceso o solicitar permiso escrito de redistribución.
