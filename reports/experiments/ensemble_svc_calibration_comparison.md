# Comparación de calibración del SVC RBF para ensemble

Fecha: 2026-07-27

Responsable: I4

Alcance: `train` para ajuste/calibración y `validation` para comparación; test protegido no utilizado.

| Configuración | Macro-F1 validation | Gap macro-F1 | Log loss | ECE top-label | Decisión |
|---|---:|---:|---:|---:|---|
| Sigmoid + `TimeSeriesSplit(5)` + `ensemble=True` | 0,203521 | 0,084552 | 1,041029 | 0,096537 | Descartada: bajo macro-F1 y gap superior a 0,05 |
| Sigmoid + `StratifiedKFold(5)` + `ensemble=False` | 0,394008 | 0,000000 | 1,016699 | 0,037618 | Descartada: mejora calibración, pero perjudica la métrica principal |
| Temperature + `StratifiedKFold(5)` + `ensemble=False` | 0,484859 | 0,007564 | 1,051532 | 0,070104 | Seleccionada: mejor macro-F1 y calibración multiclase nativa |

La configuración seleccionada conserva el SVC RBF como familia diferenciada, genera probabilidades que suman uno y cumple el umbral de generalización. Su incorporación al ensemble final sigue sujeta a comparación conjunta en T-4.1.
