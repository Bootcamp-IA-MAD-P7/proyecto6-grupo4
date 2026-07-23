# ADR 0002 — Propuesta de protocolo de evaluación (T-0.4)

- Estado: propuesta pendiente de aprobación cruzada de I1, I3 e I4 (T-0.3 confirmada por representante del equipo en sesión de 2026-07-23; falta ratificación explícita de I1/I3/I4 sobre esta propuesta concreta).
- Fecha: 2026-07-23.
- Responsable: I2.
- Revisor: I1.
- Tareas relacionadas: T-0.4, T-0.5, T-1.5, T-1.8.

## Contexto

`reports/laliga_eda.md` confirma un desbalance moderado del target `result_ft` (H 47,2 %, D 25,6 %, A 27,2 %; ratio mayoritaria/minoritaria 1,84) y un cambio temporal en la tasa de victoria local entre temporadas. El propio informe recomienda no usar accuracy en solitario y aplicar particiones cronológicas. `2_spec.md` deja pendiente la métrica principal, la fórmula de overfitting y la estrategia de partición.

## Decisión propuesta

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

Propuesta de corte (a validar con conteo exacto de filas por temporada al implementar T-1.5):

- Entrenamiento: temporadas más antiguas hasta ~2021-22 (~25 de 31 temporadas).
- Validación: 2022-23 y 2023-24.
- Test final (protegido, un solo uso): 2024-25 y 2025-26.

Esto implica una desviación respecto a la estratificación "cuando resulte apropiada" mencionada en `2_spec.md`: aquí se prioriza el orden cronológico sobre la estratificación por clase, dado el hallazgo del EDA. Se señala explícitamente para que el equipo la apruebe o la corrija.

### Semilla

`seed = 42` para todo componente estocástico (inicialización de modelos, validación cruzada, mezclas internas). El corte de partición en sí es determinista por fecha, no aleatorio.

## Evidencia de respaldo

- `reports/laliga_eda.md`, sección 4 ("Distribución y balance del target") y sección 5 (tendencia de ventaja local por temporada).
- `reports/metrics/eda_summary.json`.

## Consecuencias

- Ningún candidato (A, B, C, D) podrá compararse con una métrica o partición distinta a esta propuesta una vez aprobada.
- El test final se evalúa una sola vez tras seleccionar el Champion (T-2.6); no se reutiliza para tuning.
- Si el equipo rechaza la partición cronológica, esta ADR debe corregirse antes de ejecutar T-1.5.

## Pendientes antes de aprobar

- Ratificación explícita de I1, I3 e I4 sobre métrica, overfitting y partición.
- Validar los cortes de temporada con conteos reales de filas al construir T-1.5.
- Confirmar que T-0.2 (licencia del dataset) no obliga a cambiar de dataset, lo que invalidaría esta propuesta.

Hasta resolver estos puntos, T-0.4 permanece en `[~]` y no se inicia T-1.5 ni el entrenamiento de candidatos.
