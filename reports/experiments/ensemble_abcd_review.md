# T-4.1 — Ensemble de los 4 candidatos (A+B+C+D) vs. individuales

## Alcance

Segunda iteración de T-4.1, después de que la primera (solo A+D) quedara sin
fusionar. Esta vez se combinan los **cuatro** candidatos, pero antes de
ensamblarlos se corrigieron los dos que estaban descalificados:

- **B (I2)**: retunado (adelanto de T-4.2 aplicado solo a este candidato).
  `HistGradientBoostingClassifier` con `early_stopping=True`,
  `max_leaf_nodes=19`, `min_samples_leaf=20`, `l2_regularization=0.5`,
  `class_weight="balanced"`. Búsqueda por grid search (256 combinaciones)
  sobre `validation`, igual que el resto de candidatos (`not_applied_temporal_holdout_only`).
  **Gap 0.376 → 0.042.**
- **C (I3)**: fix ya aportado por I3 en una rama separada (`fix(ml): Actualizar
  Modelo C...`, commit `ffea77e`), traído a esta rama por cherry-pick.
  `RandomForestClassifier` regularizado (`max_depth=6`, `min_samples_leaf=15`,
  `min_samples_split=30`). **Gap 0.256 → 0.000.**

Con los cuatro ya dentro del límite de overfitting (`< 0.05`), se combinan
por votación suave. Cada candidato conserva su propio preprocesamiento
aprobado (A/C/D usan one-hot de equipos, algunos con escalado; B usa
codificación ordinal), así que el ensemble es un `VotingClassifier` de
cuatro pipelines completos, no un único preprocesamiento compartido.

Mismo dataset (SHA `6288a872…921b0c`), mismas features
(`historical_features_v1`, SHA `563634a7…8d2c81`) y mismo split que el resto.
Ajustado solo en `train` (9.607 filas), medido en `validation` (1.197 filas);
`test` no se toca.

## Resultado

| Candidato | Validation macro-F1 | Gap | Estado |
|---|---:|---:|---|
| A (logística, I1) | 0.464836 | 0.000000 | ready_for_comparison |
| B (HistGB retunado, I2) | 0.479108 | 0.042046 | ready_for_comparison (antes: disqualified, gap 0.376) |
| C (RandomForest regularizado, I3) | 0.474194 | 0.000000 | ready_for_comparison (antes: disqualified, gap 0.256) |
| **D (SVC RBF, Champion vigente)** | **0.483744** | 0.009166 | ready_for_comparison |
| Ensemble A+B+C+D | 0.454825 | 0.027714 | — |

## Interpretación

Con los cuatro candidatos ya sanos (ningún sobreajuste), el panorama es
distinto al de la primera iteración: **los cuatro individuales están muy
cerca entre sí** (0.4648–0.4837), y **D sigue siendo el mejor** por un margen
pequeño pero consistente sobre los otros tres.

El ensemble de 4 vuelve a quedar **por debajo de todos los individuales
salvo A**. Es el mismo patrón que en el ensemble A+D: promediar
`predict_proba` entre modelos con `class_weight="balanced"` diluye el
equilibrio entre clases que cada modelo por separado ya logra, penalizando
macro-F1 aunque el conjunto sea más "prudente" en promedio. Incluir dos
modelos adicionales (B y C) con calibraciones de probabilidad distintas
(HistGB y RandomForest no calibran sus probabilidades de la misma forma que
SVC o la logística) parece diluir aún más la señal en vez de reforzarla.

El gap del ensemble (0.0277) es saludable — no hay sobreajuste nuevo — pero
eso no compensa la pérdida de macro-F1.

## Decisión

**El ensemble no desplaza al Champion D.** Bajo la métrica principal
aprobada en T-0.4 (macro-F1), D sigue siendo la mejor opción individual y
también supera al ensemble completo. No se propone ningún cambio de
Champion.

## Lo que sí queda como ganancia real de este trabajo

Aunque el ensemble no gane, el ejercicio de T-4.1 **sí mejoró el proyecto**:
dos candidatos que estaban descalificados por sobreajuste severo (B: gap
0.376, C: gap 0.256) ahora cumplen el contrato (`< 0.05`) y son comparables.
B en particular pasó de ser el peor candidato con diferencia a quedar a solo
0.005 de macro-F1 del Champion.

## Sugerencias para seguir (no ejecutadas aquí)

1. **Probar `voting="hard"` o pesos distintos** (`weights=[...]`) en vez de
   promediar probabilidades por igual — podría evitar la dilución observada.
2. **Ensemble solo de los dos mejores tras el retune** (D + B, o D + C) en
   vez de los cuatro, replicando el patrón ya visto en el ensemble A+D.
3. **Calibrar B y C** con `CalibratedClassifierCV`, como ya hizo I4 con D en
   `src/ensemble/svc_calibrated.py`, antes de promediar sus probabilidades —
   la falta de calibración cruzada entre modelos de naturaleza distinta
   (árboles vs. margen vs. lineal) puede ser la causa real de la dilución.
4. Si ninguna variante de ensemble supera a D, **T-4.2 (validación cruzada y
   tuning)** debería enfocarse en seguir afinando D directamente en vez de
   insistir en el ensemble.

## Evidencia

- Métricas: `reports/experiments/ensemble_abcd_metrics.json`
- Matriz de confusión: `reports/experiments/ensemble_abcd_validation_confusion_matrix.json`
- Tabla: `reports/experiments/ensemble_table.csv` (fila `ENSEMBLE_ABCD`)
- Artefacto: `models/ensemble/ensemble_abcd_soft_voting_v1.joblib` (no versionado)
- Reproducción: `./.venv/Scripts/python.exe scripts/run_ensemble_abcd.py`
- Modelo B retunado: `src/candidates/model_b/pipeline.py`, reproducible con `./.venv/Scripts/python.exe scripts/run_candidate_b.py`
- Modelo C regularizado: aporte de I3, commit `ffea77e` (cherry-pick)
