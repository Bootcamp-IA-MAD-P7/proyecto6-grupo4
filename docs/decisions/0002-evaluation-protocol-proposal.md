# ADR 0002 — Contrato de protocolo de evaluación (T-0.4)

- Estado: contrato aprobado en T-0.4 y particiones cronológicas cerradas en T-1.5, con ratificación registrada el 24/07/2026.
- Fecha: 2026-07-23.
- Responsable: I2.
- Revisor: I1.
- Tareas relacionadas: T-0.4, T-0.5, T-1.5, T-1.8.

## Contexto

`reports/laliga_eda.md` confirma un desbalance moderado del target `result_ft` (H 47,2 %, D 25,6 %, A 27,2 %; ratio mayoritaria/minoritaria 1,84) y un cambio temporal en la tasa de victoria local entre temporadas. El propio informe recomienda no usar accuracy en solitario y aplicar particiones cronológicas. `2_spec.md` fija el contrato aprobado por los cuatro integrantes.

## Contrato aprobado

### Métrica principal

`macro-F1` (media no ponderada de F1 por clase H/D/A). Justificación: trata las tres clases como igual de importantes, evita que la clase mayoritaria (H) domine el resultado como ocurriría con accuracy, y es sensible tanto a precisión como a recall por clase — relevante porque un modelo que nunca predice `D` puede tener accuracy alta pero es inútil para el caso de uso.

### Métricas secundarias

- Accuracy (comparabilidad directa con las referencias descriptivas del EDA: baseline mayoritaria 47,2 % y favorito de apertura 54,5 %).
- Balanced accuracy.
- Precisión, recall y F1 por clase (H, D, A), con atención especial a `D` (clase minoritaria e históricamente más difícil de predecir en fútbol).
- Log loss (mide calibración de probabilidades; la aplicación deberá mostrar confianza, no solo la clase).
- Matriz de confusión 3x3 en validación y en test final.

### Fórmula de overfitting

`gap = métrica_train − métrica_validación`, calculado sobre `macro-F1`, en puntos absolutos (escala 0–1).

- Umbral de aprobación: `gap < 0.05`.
- Con validación cruzada: se reporta la media y desviación estándar de `macro-F1` en folds de entrenamiento y en folds de validación; el gap se calcula sobre las medias. Un fold individual con gap > 0.08 se documenta como observación aunque la media cumpla el umbral.
- El gap se calcula únicamente entre train y validación. El test final no participa en esta fórmula ni en ninguna decisión de ajuste.

### Estrategia de partición

Partición **cronológica por temporada**, no aleatoria ni estratificada, porque:

- El EDA detecta variación de la tasa de victoria local entre temporadas y advierte explícitamente sobre evaluar con información futura.
- El caso de uso real es predecir partidos futuros con datos pasados; una partición aleatoria filtraría señal temporal hacia el pasado (leakage temporal).

Ventanas canónicas, verificadas al implementar T-1.5:

- Entrenamiento: 1995-96–2019-20 (9.607 filas).
- Validación: 2020-21–2022-23 (1.197 filas).
- Test final (protegido, un solo uso): 2023-24–2025-26 (1.140 filas).

Se prioriza el orden cronológico sobre la estratificación por clase, dado el hallazgo del EDA. La alternativa previa con train hasta 2021-22 queda sustituida por estas ventanas canónicas.

### Semilla

`seed = 42` para todo componente estocástico (inicialización de modelos, validación cruzada, mezclas internas). El corte de partición en sí es determinista por fecha, no aleatorio.

## Evidencia de respaldo

- `reports/laliga_eda.md`, sección 4 ("Distribución y balance del target") y sección 5 (tendencia de ventaja local por temporada).
- `reports/metrics/eda_summary.json`.

## Consecuencias

- Ningún candidato (A, B, C, D) podrá compararse con una métrica o partición distinta a esta propuesta una vez aprobada.
- El test final se evalúa una sola vez tras seleccionar el Champion (T-2.6); no se reutiliza para tuning.
- Si el equipo rechaza la partición cronológica, esta ADR debe corregirse antes de ejecutar T-1.5.

## Evidencia de cierre

Los cortes fueron validados al implementar T-1.5: train 9.607 filas, validación 1.197 y test protegido 1.140. I1 verificó el 23/07/2026 el SHA-256 del dataset, la regeneración de los 11.944 índices, la ausencia de IDs duplicados o ausentes y la suite completa 14/14. T-0.2b, T-0.4 y T-1.5 constan cerrados; `Data Ready` continúa abierto por el resto de tareas pendientes de Fase 0 y Fase 1.
