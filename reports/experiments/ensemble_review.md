# T-4.1 — Ensemble A+D (votación suave) vs. candidatos individuales

## Alcance

Se combinó, por votación suave (promedio de `predict_proba`), a los dos únicos
candidatos que superaron el gap de overfitting en T-2.5: **A** (logística
multinomial) y **D** (SVC RBF, Champion vigente). No se incluyeron B ni C
(descalificados por sobreajuste) para no arrastrar ese problema al ensemble.
No se reajustó ningún hiperparámetro: `train_ensemble` reutiliza exactamente
la configuración ya aprobada de A y D (el ajuste fino es alcance de T-4.2).

Mismo dataset (SHA `6288a872…921b0c`), mismas features
(`historical_features_v1`, SHA `563634a7…8d2c81`) y mismo split
(`reports/metrics/split_manifest.json`) que A-D. Ajustado solo en `train`
(9.607 filas), medido en `validation` (1.197 filas); `test` no se toca.

## Resultado

| Candidato | Validation macro-F1 | Gap | Validation accuracy | Validation log loss |
|---|---:|---:|---:|---:|
| A (logística) | 0.464836 | 0.000000 | 0.501253 | 1.020879 |
| D (SVC RBF, Champion) | **0.483744** | 0.009166 | 0.496241 | 1.009429 |
| **Ensemble A+D** | 0.431291 | 0.016469 | **0.527987** | **1.001380** |

## Interpretación

El ensemble **no mejora la métrica principal** (macro-F1) respecto al Champion
D ni respecto a A: queda por debajo de ambos. Sí mejora `accuracy` y
`log_loss`, lo cual es consistente con un efecto conocido de la votación
suave — al promediar dos modelos con `class_weight="balanced"`, el ensemble
se vuelve algo más conservador hacia la clase mayoritaria (`H`), ganando
acierto global pero perdiendo equilibrio entre clases, que es justo lo que
macro-F1 penaliza.

El gap de overfitting del ensemble (0.0165) es saludable y está entre el de A
(0.0000) y el de D (0.0092), así que no hay señal de sobreajuste nuevo.

## Decisión

Con la métrica principal aprobada en T-0.4 (macro-F1), **el ensemble no
desplaza al Champion D**. Se documenta como comparación completada de T-4.1;
no se propone como candidato a Champion. Queda como evidencia de que combinar
A+D no aporta bajo esta métrica, con esta estrategia de votación y sin
reajuste — abre la puerta a que T-4.2 explore si un tuning de A o D (o pesos
distintos en la votación) cambia esta conclusión.

## Evidencia

- Métricas: `reports/experiments/ensemble_metrics.json`
- Matriz de confusión: `reports/experiments/ensemble_validation_confusion_matrix.json`
- Tabla de experimentos (separada de la tabla bloqueada A–D): `reports/experiments/ensemble_table.csv`
- Artefacto: `models/ensemble/ensemble_ad_soft_voting_v1.joblib` (no versionado, `.gitignore` estándar de `models/**/*.joblib`)
- Reproducción: `./.venv/Scripts/python.exe scripts/run_ensemble.py`
