# Informe técnico inicial — Nivel Esencial

El sistema predice `H`, `D` o `A` antes del partido. El EDA y sus once figuras están en `reports/laliga_eda.md` y `reports/figures/`.

## Datos y evaluación

Se usan 11.944 partidos de LaLiga. La partición temporal fija es train 9.607, validation 1.197 y test 1.140. `historical_features_v1` calcula forma de cinco partidos, goles, puntos, victorias, descanso y Elo exclusivamente con fechas anteriores. Su manifest fija el SHA de datos `6288a…921b0c` y el SHA de features `563634…8d2c81` (histórico; ver actualización de 2026-07-30 más abajo para el dataset vigente).

## Comparación y Champion (estado al cierre del Nivel Esencial, 2026-07-26)

| Candidato | Validation macro-F1 | Gap | Decisión |
|---|---:|---:|---|
| A, logística | 0.464836 | 0.000000 | Comparable |
| B, gradient boosting | 0.377080 | 0.376171 | Descartado: sobreajuste |
| C, random forest | 0.455336 | 0.261803 | Descartado: sobreajuste |
| D, SVC RBF | 0.483744 | 0.009166 | Champion |

D se reentrenó con train+validation y se evaluó una sola vez sobre test: macro-F1 0.470529, accuracy 0.486842, balanced accuracy 0.475724 y log loss 0.988387.

## Actualización — Fase 4 (Nivel Medio), 2026-07-28

Tras T-4.1/T-4.2, B se retunó (gap 0.376 → 0.042) y C se regularizó (gap
0.261 → 0.000): los cuatro candidatos quedaron sin sobreajuste. D se
recalibró (I4, `CalibratedClassifierCV`), y un ensemble por votación suave
de los cuatro candidatos ya sanos superó a todos los individuales:

| Candidato | Validation macro-F1 | Gap |
|---|---:|---:|
| A | 0.464836 | 0.000000 |
| B (retunado) | 0.479108 | 0.042046 |
| C (regularizado) | 0.474194 | 0.000000 |
| D (calibrado) | 0.484859 | 0.007564 |
| **Ensemble A+B+C+D (Champion actual)** | **0.488281** | **0.003112** |

El **Champion vigente es `ENSEMBLE_ABCD`**, reentrenado en train+validation.
Las métricas de test de esta tabla (macro-F1 0.479580, accuracy 0.506140,
balanced accuracy 0.485882, log loss 1.010428) son **evidencia histórica
congelada** de esa evaluación puntual del 2026-07-27, sobre el dataset de
entonces (SHA `6288a…921b0c`): el protocolo del proyecto evalúa el test
protegido una única vez por Champion y no se recalcula solo para
documentación (`reports/experiments/champion_test_metrics.json`,
`historical_test_evidence.status = "frozen_not_recomputed"` en
`champion_metadata.json`). Metadata completa, matriz de confusión y
detalle de la comparación en `reports/experiments/champion_metadata.json`
y `reports/experiments/ensemble_abcd_review.md`.

## Actualización — corrección de datos y re-tuning de B, 2026-07-30

Se detectó y corrigió un error de datos: la temporada 1998-99 usaba
"Villareal" (typo) como equipo distinto de "Villarreal" en el resto del
histórico, fragmentando su Elo y rachas. Tras normalizar el alias y
reentrenar todo el pipeline, el gap de B subió por encima del umbral 0.05;
se implementó una búsqueda reproducible de hiperparámetros
(`scripts/tune_candidate_b.py`, 256 combinaciones) que encontró una
configuración mejor (`l2_regularization` 0.5→1.0) con mejor macro-F1 y gap
otra vez sano. Con el dataset y B corregidos:

| Candidato | Validation macro-F1 | Gap |
|---|---:|---:|
| A | 0.464650 | 0.000000 |
| B (re-tuneado, l2=1.0) | 0.472090 | 0.049863 |
| C | 0.478792 | 0.000000 |
| D (calibrado) | 0.482867 | 0.010135 |
| **Ensemble A+B+C+D (Champion vigente)** | **0.485252** | **0.005385** |

Dataset vigente: SHA `56e59efa…607104`. Artefacto vigente: SHA
`f9c0e933…7d5696`. El test protegido **no se reevaluó** en esta actualización
(sigue congelado del 2026-07-27, ver sección anterior); una nueva evaluación
de test queda reservada para una versión final formalmente aprobada por el
equipo, no para cada corrección de datos.

## Errores y limitaciones

El Champion confunde especialmente empates con resultados locales o visitantes. No usa cuotas ni datos de lesiones, clima o estadísticas del partido actual. Equipos sin historial parten de valores cold-start. La predicción es orientativa, no una recomendación de apuesta. Al ser un ensemble de 4 modelos, la latencia de inferencia es mayor que la de un candidato individual (aunque sigue siendo del orden de milisegundos por predicción).

## Integración y verificación

FastAPI carga el pipeline completo (ahora el ensemble de 4) y genera las mismas features que entrenamiento; no requirió cambios de código al cambiar el Champion, porque usa `predict_proba`/`classes_` de forma genérica. El frontend consume el contrato versionado `/api/v1/predictions`, que incluye límite de payload (4 KiB → `413`), distinción de JSON malformado (`400`) y logging estructurado por petición. La suite completa pasa 91 pruebas.
