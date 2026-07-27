# Informe técnico inicial — Nivel Esencial

El sistema predice `H`, `D` o `A` antes del partido. El EDA y sus once figuras están en `reports/laliga_eda.md` y `reports/figures/`.

## Datos y evaluación

Se usan 11.944 partidos de LaLiga. La partición temporal fija es train 9.607, validation 1.197 y test 1.140. `historical_features_v1` calcula forma de cinco partidos, goles, puntos, victorias, descanso y Elo exclusivamente con fechas anteriores. Su manifest fija el SHA de datos `6288a…921b0c` y el SHA de features `563634…8d2c81`.

## Comparación y Champion

| Candidato | Validation macro-F1 | Gap | Decisión |
|---|---:|---:|---|
| A, logística | 0.464836 | 0.000000 | Comparable |
| B, gradient boosting | 0.377080 | 0.376171 | Descartado: sobreajuste |
| C, random forest | 0.455336 | 0.261803 | Descartado: sobreajuste |
| D, SVC RBF | 0.483744 | 0.009166 | Champion |

D se reentrenó con train+validation y se evaluó una sola vez sobre test: macro-F1 0.470529, accuracy 0.486842, balanced accuracy 0.475724 y log loss 0.988387. La matriz de confusión y metadata están en `reports/experiments/champion_metadata.json`.

## Errores y limitaciones

El Champion confunde especialmente empates con resultados locales o visitantes. No usa cuotas ni datos de lesiones, clima o estadísticas del partido actual. Equipos sin historial parten de valores cold-start. La predicción es orientativa, no una recomendación de apuesta.

## Integración y verificación

FastAPI carga el pipeline completo y genera las mismas features que entrenamiento. El frontend consume el contrato versionado `/api/v1/predictions`. La suite esencial pasa 28 pruebas con un directorio temporal aislado.
