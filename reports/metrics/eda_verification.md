# Evidencia de verificación del EDA

Fecha: 2026-07-22  
Rama: `feature/t-1.3-laliga-eda`

## Comandos

```powershell
.\.venv\Scripts\python.exe scripts\run_laliga_eda.py
.\.venv\Scripts\python.exe scripts\create_eda_notebook.py
.\.venv\Scripts\python.exe scripts\execute_eda_notebook.py
.\.venv\Scripts\python.exe -m pytest
```

## Controles esperados

- 11.944 filas y 54 columnas.
- 31 temporadas, 1995-09-02–2026-05-24.
- 0 IDs duplicados.
- 0 targets ausentes.
- 0 incoherencias entre marcador final y `result_ft`.
- 2 filas con información de descanso incompleta, conservadas como nulas.
- 9 figuras generadas y revisadas visualmente.
- Notebook ejecutado sin excepción.
- Suite de tests aprobada: **6 passed** (3 de loader, 2 de contrato/métricas y 1 de integración completa).

La revisión cruzada humana indicada por `.specify/4_tasks.md` sigue pendiente; por ese motivo T-1.1, T-1.2 y T-1.3 permanecen en progreso.
