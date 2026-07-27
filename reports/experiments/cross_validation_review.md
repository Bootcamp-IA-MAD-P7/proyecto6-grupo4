# T-4.2 — Validación cruzada cronológica (A, B, C, D)

## Método

`src/evaluation/cross_validation.py::chronological_cv_scores` aplica
`TimeSeriesSplit(n_splits=4)` **exclusivamente sobre las filas
`split == "train"`**, ordenadas por fecha. Cada fold ajusta en una ventana
creciente de partidos pasados y mide macro-F1 en el bloque inmediatamente
posterior — el mismo patrón "solo pasado" que ya usa el generador de
features (T-1.4a), replicado a nivel de evaluación. `validation` y `test`
nunca se leen en este proceso: es una estimación de estabilidad, no un
mecanismo de selección de Champion (eso sigue siendo T-2.6, sobre
`validation` únicamente).

Reproducible con: `./.venv/Scripts/python.exe scripts/run_cross_validation.py`.

## Resultado

| Candidato | macro-F1 medio (4 folds) | Desviación estándar |
|---|---:|---:|
| A (logística) | 0.4140 | 0.0273 |
| B (HistGB retunado) | 0.4199 | 0.0343 |
| C (RandomForest regularizado) | 0.4270 | 0.0244 |
| D (SVC calibrado) | 0.4170 | 0.0382 |

Detalle por fold (los cuatro candidatos comparten el mismo patrón):

| Fold | Ventana de test | Filas de train | A | B | C | D |
|---|---|---:|---:|---:|---:|---:|
| 0 | 2000-02 – 2005-03 | 1.923 | 0.377 | 0.375 | 0.402 | 0.373 |
| 1 | 2005-03 – 2010-03 | 3.844 | 0.399 | 0.398 | 0.404 | 0.386 |
| 2 | 2010-03 – 2015-04 | 5.765 | 0.446 | 0.449 | 0.445 | 0.454 |
| 3 | 2015-04 – 2020-06 | 7.686 | 0.434 | 0.457 | 0.457 | 0.456 |

## Interpretación

1. **Los cuatro candidatos mejoran de forma consistente y monótona (o casi)
   a medida que crece la ventana de entrenamiento.** El fold 0 (apenas 1.923
   partidos de historia) da macro-F1 ~0.37-0.40 para los cuatro; el fold 3
   (7.686 partidos) da ~0.43-0.46 — muy cerca de los números de
   `validation` reportados en T-2.5/T-4.1 (0.46-0.49). Esto es evidencia de
   que el sistema necesita historial suficiente para rendir bien, algo
   coherente con el cold-start ya documentado como limitación.
2. **Ningún candidato se degrada con el tiempo** — descarta la hipótesis de
   que el fútbol español haya cambiado de forma que invalide el enfoque
   "solo histórico" dentro del rango de datos disponible.
3. **C tiene la desviación estándar más baja (0.024)** — el más estable
   entre folds. **D tiene la más alta (0.038)** — coherente con ser un
   modelo más sensible a la cantidad de datos (el SVC con kernel RBF
   necesita más ejemplos para generalizar bien el margen).
4. Los valores absolutos de CV (0.41-0.43) son más bajos que los de
   `validation` (0.46-0.49) porque los folds tempranos promedian con muy
   poco historial disponible — no es una señal de que la métrica de
   `validation` esté inflada, sino de que el propio proceso de CV incluye
   deliberadamente los peores escenarios (arranque en frío histórico).

## Consecuencia para T-4.2

No se encontró ninguna razón, a partir de la CV, para cambiar los
hiperparámetros ya elegidos para B (T-4.1) o para la calibración de D
(T-4.2 sobre D): los cuatro son estables y mejoran con más datos, sin
señales de inestabilidad temporal que ameriten una configuración distinta
por época.

## Evidencia

- `reports/experiments/candidate_{a,b,c,d}_cv_summary.json`
- `reports/experiments/experiments_table.csv` (columna `cv_summary_reference` ahora apunta a estos archivos en vez de `not_applied_temporal_holdout_only`)
- `src/evaluation/cross_validation.py`, `scripts/run_cross_validation.py`
- Tests: `tests/unit/test_cross_validation.py`
