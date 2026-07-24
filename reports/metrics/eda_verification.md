# Evidencia de verificación del EDA

Fecha: 2026-07-24
Alcance: cierre técnico I1 de T-1.1 a T-1.4

## Comandos

```powershell
.\.venv\Scripts\python.exe scripts\run_laliga_eda.py
.\.venv\Scripts\python.exe scripts\create_eda_notebook.py
.\.venv\Scripts\python.exe scripts\execute_eda_notebook.py
.\.venv\Scripts\python.exe -m pytest
```

## Controles esperados

- Dataset preprocesado: 11.944 filas y 54 columnas.
- Alcance del EDA: 10.804 filas de train+validación, 28 temporadas, 1995-09-02–2023-06-04; las 1.140 filas de test (2023-24–2025-26) quedan excluidas.
- 0 IDs duplicados.
- 0 targets ausentes.
- 0 incoherencias entre marcador final y `result_ft`.
- 2 filas con información de descanso incompleta, conservadas como nulas.
- 11 figuras generadas y revisadas visualmente.
- Notebook ejecutado sin excepción.
- Coherencia preprocesamiento/splits: misma huella SHA-256, 11.944 `match_id` cubiertos una sola vez y conteos 9.607/1.197/1.140.
- Ningún flujo de EDA, ajuste o selección carga el test: `scripts/run_laliga_eda.py` y el notebook filtran la etiqueta `test` antes de calcular métricas o figuras.
- Suite de tests aprobada: **15 passed**.

La evidencia técnica I1 está completa. Las revisiones humanas exigidas por `.specify/4_tasks.md` siguen siendo necesarias antes del cierre formal de cada tarea.
