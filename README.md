# Proyecto grupal de clasificación

Repositorio inicial para construir una solución de machine learning de clasificación con cuatro developers y cuatro modelos candidatos.

## Regla de trabajo

Antes de proponer o modificar código es obligatorio leer completamente:

1. `.specify/0_constitution.md`.
2. `.specify/1_intent.md`.
3. `.specify/2_spec.md`.
4. `.specify/3_plan.md`.
5. `.specify/4_tasks.md`.

La carpeta `.specify/` es la fuente central de verdad. El equipo ha aprobado técnicamente LaLiga, la predicción prepartido y el target multiclase `result_ft` (`H`, `D`, `A`). Siguen pendientes las condiciones de uso y redistribución de las fuentes, el protocolo de evaluación, las features comunes, los cuatro algoritmos y la arquitectura de aplicación.

## Estrategia de datos y modelos

1. Selección y conexión únicas al dataset.
2. EDA y limpieza iniciales compartidos.
3. Particiones comunes y congeladas.
4. Cuatro pipelines específicos.
5. Cuatro modelos candidatos comparables.
6. Selección e integración de un Champion.

## Ramas

- `main`: versión estable.
- `develop`: integración.
- `feature/i1-data-foundation`: frente inicial de datos.
- `feature/i2-evaluation-contract`: frente inicial de evaluación.
- `feature/i3-frontend-mock`: frente inicial de frontend.
- `feature/i4-backend-mock`: frente inicial de backend.

Después de los frentes iniciales, las ramas se crearán por ticket y se integrarán mediante Pull Request hacia `develop`.

## Estructura

- `app/`: frontend y backend.
- `data/`: datos raw, intermedios, procesados y feedback.
- `src/data/`: preparación común de datos.
- `src/candidates/`: pipelines y entrenamiento de candidatos A–D.
- `src/evaluation/`: comparación y métricas comunes.
- `models/`: artefactos candidatos, Champion y monitorización.
- `reports/`: experimentos, métricas y figuras.
- `tests/`: pruebas unitarias, de integración y end-to-end.
- `docs/`: documentación y presentaciones.

## Base de datos y EDA de LaLiga

La selección técnica y el target están aprobados. El preprocesamiento y el EDA son reproducibles y están integrados, pero no cierran `Data Ready`: falta aprobar las condiciones de uso, el protocolo temporal, las features comunes, los candidatos y las revisiones indicadas en el backlog.

Fuentes incluidas y versionadas sin modificar dentro de `data/raw/`:

- `LaLiga_Matches.csv`.
- `laliga_2025_2026_stats.csv`.

Ejecución en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-eda.txt
.\.venv\Scripts\python.exe scripts\run_laliga_preprocessing.py
.\.venv\Scripts\python.exe scripts\run_laliga_eda.py
.\.venv\Scripts\python.exe scripts\create_preprocessing_notebook.py
.\.venv\Scripts\python.exe scripts\create_eda_notebook.py
.\.venv\Scripts\python.exe scripts\execute_eda_notebook.py
.\.venv\Scripts\python.exe -m pytest
```

Entregables principales:

- `reports/laliga_eda.md`: informe interpretado.
- `notebooks/00_laliga_preprocessing.ipynb`: fuentes, columnas, limpieza y combinación.
- `notebooks/01_laliga_eda.ipynb`: EDA ejecutado desde el dataset limpio.
- `data/processed/laliga_matches_clean.csv`: dataset canónico limpio.
- `reports/figures/`: once visualizaciones persistentes.
- `reports/metrics/`: manifest, procedencia, política de columnas, auditoría, diccionario y resúmenes.
- `src/data/laliga_loader.py`: mecanismo único de carga y combinación.
