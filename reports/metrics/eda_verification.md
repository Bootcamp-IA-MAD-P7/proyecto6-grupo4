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

La evidencia técnica I1 está completa.

## Revisión cruzada I3 de T-1.2

Fecha: 2026-07-24

I3 revisó el diccionario `data_dictionary.csv`, el perfil de nulos `missingness.csv` y el resumen de auditoría `eda_summary.json`. Confirmó que las 54 variables tienen descripción, tipo, rol, rango o valores permitidos, tratamiento de nulos, disponibilidad y riesgo de leakage; que `result_ft` es el target y `match_id` no participa como predictor; y que las variables posteriores al evento, metadatos de cobertura y cuotas de cierre se tratan conforme a sus riesgos declarados.

La suite se reprodujo mediante `./.venv/Scripts/python.exe -m pytest -q`: **16 passed**. Con esta evidencia, T-1.2 queda cerrada.

## Revisión compartida I1–I4 de T-1.3

Fecha: 2026-07-24

El equipo revisó el notebook, el informe, `eda_summary.json` y las 11 figuras. Confirmó la cobertura de nulos, duplicados, target, relaciones, correlaciones, outliers y riesgos de leakage; verificó que las matrices de confusión son baselines descriptivas y que el test 2023-24–2025-26 no participa en métricas ni visualizaciones. El EDA se regeneró sobre las 10.804 filas de train+validación y la suite terminó con **16 passed**. T-1.3 queda cerrada.

## Revisión cruzada I4 de T-1.4

Fecha: 2026-07-24

I4 revisó la limpieza determinista, la política de columnas y el contrato preprocesamiento/splits. La regeneración conserva el hash `6288a872df07a196a48ea05039671feba0616489927ebc12b344d96f0e921b0c`, las 11.944 filas, 54 columnas, cero IDs duplicados, cero targets nulos y los conteos de split 9.607/1.197/1.140. Los dos nulos opcionales de descanso se mantienen sin imputar; los raw permanecen inmutables. T-1.4 queda cerrada.
