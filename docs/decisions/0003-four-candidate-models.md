# ADR 0003 — Cuatro modelos candidatos (T-0.5)

- Estado: confirmado por el equipo en daily 2026-07-24 (representante de sesión).
- Fecha: 2026-07-24.
- Responsable: I2 (coordina); todo el equipo decide.
- Tareas relacionadas: T-0.5, T-1.8, T-2.1–T-2.4.

## Contexto

`ML-02` exige cuatro candidatos comparables bajo el mismo protocolo de T-0.4, uno por integrante (Pipeline A→I1, B→I2, C→I3, D→I4), con diversidad justificada y sin duplicación injustificada.

## Decisión

| Candidato | Integrante | Algoritmo | Justificación |
|---|---|---|---|
| A | I1 | Regresión logística multinomial | Lineal, muy interpretable y rápida de entrenar; baseline para validar el contrato de datos y el generador de features antes de introducir modelos más complejos. |
| B | I2 | Gradient boosting (`HistGradientBoostingClassifier` de scikit-learn, o XGBoost/LightGBM) | Referencia de rendimiento habitual en datos tabulares; expone importancia de variables nativa, útil para el análisis de errores y la selección del Champion que coordina I2. |
| C | I3 | Random forest | Ensemble por bagging, robusto al ruido; importancia de variables fácil de comunicar en la demo de negocio sin tanta carga matemática como el boosting. |
| D | I4 | SVM con kernel RBF y probabilidades habilitadas | Paradigma distinto (margen, no árboles); modelo compacto de serializar e inferencia rápida, alineado con el foco de latencia y despliegue de I4. |

## Diversidad cubierta

Cuatro familias distintas: lineal (A), boosting de árboles (B), bagging de árboles (C) y margen (D). A y C comparten linaje de árboles de decisión (bagging vs. boosting), lo cual se considera diversidad suficiente pero no máxima; se señala explícitamente por si el equipo prefiere mayor distancia (alternativas descartadas: Naive Bayes o k-NN, con rendimiento esperado menor dado el desbalance moderado y las features mixtas del dataset).

## Consecuencias

- Cada integrante entrena su propio candidato bajo el contrato común de experimentación (`2_spec.md`).
- Ningún integrante puede cambiar su algoritmo asignado sin actualizar esta ADR y notificar al equipo.
- El Champion se elige entre estos cuatro candidatos según los criterios de `2_spec.md` (generalización, complejidad operativa, interpretabilidad, coste de inferencia), no por preferencia individual.

## Pendientes

- Confirmación individual de I1, I3 e I4 sobre su algoritmo asignado si alguno objeta la propuesta de representante.
- Ajustar hiperparámetros por defecto/rango de búsqueda cuando se implemente cada pipeline (T-2.1–T-2.4).

## Enmienda 2026-07-28 (T-4.1/T-4.2)

La consecuencia original ("El Champion se elige entre estos cuatro
candidatos") se amplía: tras corregir el sobreajuste de B y C, e integrar la
calibración de probabilidades de D (T-4.2), el ensemble por votación suave
de los cuatro (`ENSEMBLE_ABCD`) superó a los cuatro individuales en
`validation` (macro-F1 0,488281 vs. 0,484859 del mejor individual) y también
en el test protegido (macro-F1 0,479580 vs. 0,470529). A petición explícita
del equipo, se amplía la elegibilidad de Champion para incluir también el
ensemble de los cuatro candidatos aprobados, no solo cada uno por separado.
No se admite ningún candidato o ensemble fuera de A, B, C, D y su
combinación. Detalle de la selección en
`reports/experiments/champion_metadata.json` y en T-2.6 de `4_tasks.md`.
