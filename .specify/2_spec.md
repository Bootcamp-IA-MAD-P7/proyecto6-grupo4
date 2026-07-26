# SPEC 2 — Especificación técnica

## Autoridad y estado

Este documento define el contrato técnico del proyecto y está subordinado a `0_constitution.md` y `1_intent.md`. Toda implementación debe respetarlo o detenerse hasta que el equipo apruebe y documente un cambio.

Estado actual: **EDA, target, contrato de evaluación y particiones aprobados por los cuatro integrantes el 24/07/2026; T-0.2b se cerró el mismo día con la política de procedencia y redistribución documentada. El entrenamiento de candidatos sigue sujeto al resto del gate `Data Ready` (T-1.8)**.

## Requisitos obligatorios de la consigna

### Entregables

- Aplicación que reciba datos y devuelva una predicción de clasificación.
- Repositorio en GitHub con ramas ordenadas y mensajes de commit limpios.
- Informe técnico del rendimiento y explicación del modelo.
- Presentación orientada a negocio.
- Presentación técnica del código.
- Enlace a Trello u otra herramienta organizativa.

### Tecnologías indicadas

- Scikit-learn.
- Pandas.
- Streamlit, Dash o Gradio como tecnologías de interfaz indicadas por la consigna.
- Git y GitHub.
- Docker.

La consigna también menciona una API como posible mecanismo de productivización. La tecnología definitiva de aplicación deberá aprobarse antes de implementarse.

### Restricción de overfitting

Aprobada en T-0.4 (2026-07-23), ratificada en daily 2026-07-24:

- Métrica principal: `macro-F1`.
- Gap: `max(0, macro_F1_train - macro_F1_validation)`.
- Unidad: puntos absolutos de la métrica, no porcentaje relativo.
- Umbral: `gap < 0.05`.
- También se registrará `abs(macro_F1_train - macro_F1_validation)` para detectar diferencias anómalas en cualquier dirección.
- Si se usa validación temporal por ventanas o folds, se informa la media, la desviación y el peor gap; la selección no puede ocultar un fold temporal degradado.

Hasta resolver estas decisiones ningún modelo podrá declararse Champion.

## Requisitos acumulativos por nivel

### Nivel Esencial

- Modelo funcional de clasificación.
- EDA con visualizaciones relevantes.
- Overfitting inferior al 5 %.
- Solución productivizada.
- Informe con métricas de clasificación, explicación del rendimiento, importancia de variables o equivalente y análisis de errores.

### Nivel Medio

- Modelo ensemble.
- Validación cruzada.
- Optimización de hiperparámetros.
- Recogida de feedback.
- Recogida de datos nuevos para futuros reentrenamientos.

### Nivel Avanzado

- Dockerización.
- Persistencia en base de datos de los datos recogidos.
- Despliegue.
- Tests unitarios.

### Nivel Experto

- Experimento o despliegue de red neuronal.
- A/B testing.
- Monitorización de data drift.
- Reemplazo de modelo condicionado por métricas predefinidas.

Docker aparece también en la lista general de tecnologías. Por esta ambigüedad, la compatibilidad con Docker se comprobará temprano, aunque el gate formal de dockerización pertenezca al Nivel Avanzado. La interpretación definitiva deberá confirmarse con el equipo o el personal docente.

## Estado de decisiones técnicas

| Decisión | Estado | Valor |
|---|---|---|
| Dataset | Aprobada 2026-07-24 (T-0.2b, uso local) | Partidos de LaLiga 1995-96–2025-26, dos CSV locales combinados mediante loader único; uso local, permanencia de las copias ya trackeadas aceptada por el equipo, sin publicar nuevos derivados fila a fila salvo permiso escrito |
| Problema de negocio | Propuesta registrada | Predicción prepartido del resultado final; no se inicia entrenamiento hasta aprobación |
| Usuario principal | Propuesta registrada | Persona usuaria interesada en análisis deportivo prepartido |
| Target | Aprobada 2026-07-23 | `result_ft`: `H`, `D`, `A` |
| Tipo de clasificación | Aprobada 2026-07-23 | Multiclase de tres clases |
| Métrica principal | Aprobada 2026-07-23 (T-0.4) | `macro-F1` |
| Métricas secundarias | Aprobada 2026-07-23 (T-0.4) | Accuracy, balanced accuracy, precisión/recall/F1 por clase, log loss, matriz de confusión |
| Fórmula de overfitting | Aprobada 2026-07-23 (T-0.4) | `gap = macro-F1(train) − macro-F1(validación)`, en puntos absolutos; umbral `< 0.05` sobre medias de CV |
| Estrategia de partición | Aprobada 2026-07-23 (T-0.4/T-1.5) | Cronológica por temporada, congelada: train 1995-96–2019-20 (9.607 filas), validación 2020-21–2022-23 (1.197 filas), test 2023-24–2025-26 (1.140 filas, protegido); semilla `42` |
| Modelos A, B, C y D | Aprobada 2026-07-24 (T-0.5) | A: regresión logística multinomial (I1). B: gradient boosting (I2). C: random forest (I3). D: SVM kernel RBF (I4). Detalle en `docs/decisions/0003-four-candidate-models.md` |
| Tecnología frontend | Aprobada 2026-07-24 (T-0.6) | React + TypeScript con Vite; implementación propiedad de I3 |
| Tecnología backend | Aprobada 2026-07-24 (T-0.6) | FastAPI + Pydantic, servido con Uvicorn; implementación propiedad de I4 |
| Arquitectura de aplicación | Aprobada 2026-07-24 (T-0.6) | Frontend y backend separados: React consume por HTTP/JSON la API FastAPI versionada |
| Persistencia | Pendiente | No seleccionada |
| Despliegue | Pendiente | No seleccionado |
| Gestión del equipo | Aprobada | GitHub Project `Proyecto6-Grupo4`, issues #3–#35 |
| Estrategia Git | Aprobada | `main` estable, `develop` integración y ramas `feature/` por ticket |

### Spike exploratorio autorizado para T-1.1–T-1.4

Las solicitudes de 2026-07-22 y 2026-07-23 autorizaron carga, auditoría, diccionario, limpieza reproducible y EDA antes de cerrar todos los gates. Este trabajo se clasifica como spike exploratorio: produce evidencia para decidir, pero no habilita splits ni entrenamiento y no altera la regla general de dependencias.

- Dataset canónico aprobado técnicamente: `laliga_matches_1995_96_to_2025_26_v1`.
- Fuentes raw locales: `LaLiga_Matches.csv` y `laliga_2025_2026_stats.csv`; se conservan inmutables. Las URL, huellas y adquisición local reproducible están documentadas en `docs/data_acquisition.md`. El equipo ratificó en daily 2026-07-24 la permanencia de las copias ya trackeadas en Git; no hay remediación pendiente sobre este punto.
- Manifest con dimensiones y SHA-256: `reports/metrics/dataset_manifest.json`.
- Dataset limpio canónico: `data/processed/laliga_matches_clean.csv`, generado únicamente desde los dos raw por `scripts/run_laliga_preprocessing.py`.
- Evidencia del preprocesamiento: `notebooks/00_laliga_preprocessing.ipynb`, `reports/metrics/preprocessing_summary.json` y `reports/metrics/source_column_policy.csv`.
- Target aprobado: `result_ft` (`H`, `D`, `A`).
- Resultado de auditoría: 11.944 filas, 54 columnas, 31 temporadas, 0 IDs duplicados, 0 targets nulos y 0 incoherencias marcador/resultado.
- EDA reproducible: `reports/laliga_eda.md`, `notebooks/01_laliga_eda.ipynb` y once figuras persistentes.
- Las matrices de confusión de esta fase corresponden exclusivamente a reglas descriptivas fijas (clase mayoritaria y favorito de apertura); no son candidatos entrenados ni sustituyen T-0.4.
- Procedencia y revisión I1 documentadas: el uso analítico local encaja con la finalidad declarada. El equipo ratificó en daily 2026-07-24 (I2/I3/I4) mantener las copias ya trackeadas sin remediación adicional.

## Estrategia Git aprobada

### Ramas permanentes

- `main`: versión estable, demostrable y potencialmente entregable.
- `develop`: rama de integración del trabajo revisado.

No se trabajará directamente sobre estas ramas salvo una operación de bootstrap aprobada por el equipo. El cambio que crea la estructura inicial constituye esa operación excepcional.

### Ramas de trabajo

Las ramas de trabajo serán temporales y estarán asociadas a un ticket de `4_tasks.md`.

Formato general:

```text
feature/t-<fase>.<tarea>-<descripcion-corta>
```

Ejemplos posteriores:

```text
feature/t-1.1-dataset-loader
feature/t-2.1-model-a
feature/t-3.3-frontend-integration
```

Para iniciar los cuatro frentes se crean estas ramas:

- `feature/i1-data-foundation`.
- `feature/i2-evaluation-contract`.
- `feature/i3-frontend-mock`.
- `feature/i4-backend-mock`.

Estas ramas iniciales no son ramas personales permanentes. Se cerrarán después de integrar las tareas iniciales y las siguientes ramas se crearán por ticket.

### Flujo de integración

1. Actualizar la rama de trabajo desde `develop` antes de comenzar.
2. Implementar únicamente el ticket asignado.
3. Ejecutar pruebas y registrar evidencia.
4. Abrir Pull Request hacia `develop`.
5. Obtener al menos una revisión de otra persona.
6. Integrar solo con criterios de aceptación satisfechos.
7. Eliminar la rama temporal después del merge.
8. Promover `develop` a `main` mediante Pull Request cuando exista un gate estable.

No se permiten pushes directos a `main` ni a `develop` después del bootstrap. Los cambios urgentes deberán utilizar una rama temporal y revisión.

### Convención de commits

Los commits serán pequeños y descriptivos. Prefijos recomendados:

- `feat:` funcionalidad.
- `fix:` corrección.
- `docs:` documentación.
- `test:` pruebas.
- `refactor:` reestructuración sin cambio funcional.
- `chore:` mantenimiento.

## Estructura objetivo del repositorio

La estructura inicial es neutral respecto del dataset, los cuatro algoritmos y los frameworks de frontend/backend:

```text
.
|-- .github/
|   |-- workflows/
|   `-- pull_request_template.md
|-- .specify/
|   |-- 1_intent.md
|   |-- 2_spec.md
|   |-- 3_plan.md
|   |-- 4_tasks.md
|   `-- 5_dataset.md
|-- app/
|   |-- backend/
|   `-- frontend/
|-- config/
|-- data/
|   |-- raw/
|   |-- interim/
|   |-- processed/
|   `-- feedback/
|-- docker/
|-- docs/
|   |-- business_presentation/
|   |-- decisions/
|   |-- project_management/
|   `-- technical_presentation/
|-- models/
|   |-- candidates/
|   |   |-- model_a/
|   |   |-- model_b/
|   |   |-- model_c/
|   |   `-- model_d/
|   |-- champion/
|   `-- monitoring/
|-- notebooks/
|-- reports/
|   |-- experiments/
|   |-- figures/
|   `-- metrics/
|-- scripts/
|-- src/
|   |-- candidates/
|   |   |-- model_a/
|   |   |-- model_b/
|   |   |-- model_c/
|   |   `-- model_d/
|   |-- common/
|   |-- data/
|   |-- evaluation/
|   |-- inference/
|   `-- mlops/
|-- tests/
|   |-- e2e/
|   |-- fixtures/
|   |-- integration/
|   `-- unit/
|-- .gitignore
`-- README.md
```

Responsabilidades de las áreas principales:

- `data/raw/`: datasets originales inmutables; la trazabilidad y la política de uso se conservan en el manifest de procedencia.
- `data/interim/`: resultados intermedios reproducibles.
- `data/processed/`: base común posterior a las reglas aprobadas.
- `src/data/`: conexión, auditoría y limpieza comunes.
- `src/candidates/model_*`: pipeline y entrenamiento específicos de cada candidato.
- `models/candidates/model_*`: artefactos candidatos; inicialmente ignorados por Git salvo marcador.
- `src/evaluation/`: métricas, overfitting y comparación común.
- `app/frontend/` y `app/backend/`: separación lógica preparada sin imponer frameworks.
- `src/inference/`: carga del Champion y lógica de inferencia compartida.
- `src/mlops/` y `models/monitoring/`: componentes opcionales de niveles superiores.
- `reports/`: evidencia generada, métricas, experimentos y figuras.
- `tests/`: pruebas separadas por alcance.

No se crearán implementaciones dentro de estas carpetas hasta que exista un ticket autorizado y se hayan resuelto sus decisiones técnicas.

## Estrategia común de datos

### Dataset canónico

El dataset canónico técnicamente aprobado es `laliga_matches_1995_96_to_2025_26_v1`. Combina `LaLiga_Matches.csv` y `laliga_2025_2026_stats.csv` mediante `src/data/laliga_loader.py`. La versión procesada común es `data/processed/laliga_matches_clean.csv`; su metadata y huellas viven en `reports/metrics/`.

La aprobación técnica y la revisión de procedencia constan documentadas. T-0.2b está cerrada; el resto de requisitos de `Data Ready` se gestionan en sus tareas correspondientes.

El dataset original deberá:

- Mantenerse inmutable.
- Tener una fuente y licencia documentadas.
- Tener una variable objetivo categórica clara.
- Permitir una decisión o historia de negocio comprensible.
- Ser suficiente para separar entrenamiento, validación y test.
- Evitar datos sensibles innecesarios.
- Permitir una aplicación con inputs disponibles antes de la predicción.

No se crearán cuatro mecanismos independientes de conexión o cuatro versiones incompatibles del dataset.

### Contrato común de features prepartido

Los cuatro candidatos consumirán una tabla de features generada por una única implementación común:

| Grupo | Regla |
|---|---|
| Inputs directos | `home_team`, `away_team`, `match_date`; `match_time` solo si se aprueban su cobertura y tratamiento |
| Features históricas | Forma reciente, puntos, goles a favor/en contra, fuerza o rating; siempre calculadas con filas anteriores |
| Cuotas de apertura | Experimento opcional separado; no pueden ser requisito del MVP porque solo cubren 380 partidos |
| Cuotas de cierre | Excluidas del MVP por riesgo de disponibilidad temporal |
| Encuentro actual | Excluidos goles, resultado, tiros, faltas, córners, tarjetas y todas sus derivadas |
| Metadatos | `match_id` y proxies de fuente o cobertura quedan fuera del modelo |

Implementación versionada: `src/data/historical_features.py` genera
`historical_features_v1`. Usa una ventana de cinco encuentros, puntos, goles a
favor/en contra, tasa de victorias, días desde el último partido y Elo
(`1500`, factor K `20`). Las filas se ordenan de forma estable por
`match_date` y `match_id`, pero se calculan por lotes de fecha: todas las
features de la fecha se emiten antes de incorporar sus resultados. De este modo
un partido del mismo día tampoco se considera pasado de otro. `match_id`,
`season`, `match_date`, `split` y `result_ft` permanecen como metadata y no se
entregan al estimador. La regeneración local se realiza con
`python scripts/run_historical_features.py` y su evidencia queda en
`reports/metrics/historical_features_manifest.json`.

Reglas obligatorias:

- Toda agregación histórica aplica `shift(1)` o una operación equivalente antes de cualquier ventana.
- El cálculo recorre los partidos en orden cronológico estable.
- Los parámetros de imputación, codificación y escalado se ajustan solo con entrenamiento.
- Una prueba de no-leakage demuestra que modificar un resultado futuro no cambia las features de partidos anteriores.
- La tabla común se versiona con schema, rango temporal, generador y SHA-256.

### EDA y limpieza comunes

Se realizará una única fase compartida de EDA y limpieza inicial. Todos los integrantes contribuirán al análisis; el Integrante 1 coordinará la consolidación técnica.

El EDA deberá cubrir como mínimo:

- Dimensiones y tipos.
- Nulos y duplicados.
- Distribución del target.
- Posible desbalance.
- Distribuciones de variables.
- Valores extremos.
- Relaciones con el target.
- Correlaciones cuando sean pertinentes.
- Identificadores sin valor predictivo.
- Variables posteriores al evento o con leakage.
- Viabilidad de convertir variables en entradas de aplicación.

Las reglas comunes de limpieza deberán quedar codificadas y documentadas. Ningún integrante podrá limpiar o eliminar observaciones de forma diferente para favorecer su modelo.

Se permiten diagnósticos adicionales específicos por modelo, siempre que no alteren la base común sin aprobación.

### Contrato de datos

Antes de entrenar deberá documentarse para cada variable:

- Nombre técnico.
- Descripción.
- Tipo.
- Rol: feature, target, identificador o excluida.
- Valores o rango permitidos.
- Tratamiento común de nulos.
- Disponibilidad en el momento de inferencia.
- Riesgo de leakage o sensibilidad.

### Particiones congeladas

Las particiones de entrenamiento, validación y test se generarán una sola vez y serán utilizadas por los cuatro candidatos.

Requisitos:

- Orden cronológico por `match_date` y clave estable de desempate.
- Ventanas temporales explícitas y sin solapamiento.
- Congelado en T-1.5 (ratificado 2026-07-24): train 1995-96–2019-20 (9.607 filas); validación 2020-21–2022-23 (1.197 filas); test 2023-24–2025-26 (1.140 filas, protegido). Implementado en `src/evaluation/splits.py`, versionado en `data/processed/splits/laliga_splits.csv` y `reports/metrics/split_manifest.json`.
- La semilla (`42`) solo controla algoritmos y operaciones internas; no decide el split principal.
- La estratificación aleatoria por filas no sustituye la separación temporal.
- Índices o mecanismo de generación versionados.
- Test final reservado.
- Transformaciones ajustadas únicamente con entrenamiento.
- Posible backtesting adicional con ventanas temporales expansivas, sin consultar el test final.

**Regla de re-congelado:** cualquier cambio en las reglas comunes de limpieza de `T-1.4` (o en los CSV raw de origen) invalida automáticamente el SHA-256 registrado en `reports/metrics/split_manifest.json`. Antes de considerar vigente `T-1.5`, hay que volver a ejecutar `scripts/run_laliga_preprocessing.py` y `python -m src.evaluation.splits`, y reconfirmar: mismo SHA-256 y 11.944 `match_id`; mismos cortes por temporada (train 1995-96–2019-20, validación 2020-21–2022-23, test 2023-24–2025-26); mismos conteos 9.607/1.197/1.140. Si algún valor cambia, `T-1.5` vuelve a `[~]` hasta nueva revisión cruzada de I1, I3 e I4.

El Integrante 2 coordinó este contrato con revisión técnica del Integrante 1 y revisión cruzada de I3/I4 ratificada en daily 2026-07-24.

### Gate `Data Ready`

No podrá comenzar el entrenamiento individual hasta verificar:

- [x] Dataset seleccionado y accesible localmente.
- [x] Condiciones de uso y redistribución aprobadas (uso local ratificado 2026-07-24, incluida la permanencia de los CSV ya trackeados en Git).
- [x] Target y clases aprobados.
- [x] EDA inicial completado (T-1.3: revisión compartida I1–I4 el 2026-07-24).
- [x] Reglas comunes de limpieza aprobadas (T-1.4: revisión I2/I4; regeneración y contrato de splits verificados el 2026-07-24).
- [x] Variables con leakage excluidas técnicamente por el contrato y el generador histórico (pendiente de ratificación de I2 dentro de T-1.4a).
- [ ] Generador común de features históricas aprobado y probado (T-1.4a, bloqueante de `Data Ready`).
- [x] Contrato de datos aprobado (T-1.2: diccionario y auditoría revisados por I3 el 2026-07-24).
- [x] Particiones comunes reproducibles.
- [x] Test final protegido.
- [x] Métricas comunes definidas.
- [x] Fórmula de overfitting definida.
- [x] Cuatro modelos candidatos aprobados.

## Pipelines individuales

Cada integrante desarrollará un pipeline completo orientado a su modelo:

- Integrante 1: Pipeline A + Modelo A.
- Integrante 2: Pipeline B + Modelo B.
- Integrante 3: Pipeline C + Modelo C.
- Integrante 4: Pipeline D + Modelo D.

Los pipelines podrán diferir en:

- Imputación específica.
- Codificación.
- Escalado.
- Selección de variables.
- Transformaciones matemáticas.
- Balanceo aplicado solo sobre entrenamiento.
- Hiperparámetros y estimador.

Todos deberán:

- Consumir el mismo contrato de datos.
- Usar las mismas particiones.
- Respetar las exclusiones comunes.
- Encapsular las transformaciones necesarias para inferencia.
- Ajustar transformaciones solo con entrenamiento.
- Ser reproducibles.
- Guardar el pipeline completo junto con el estimador.
- Producir predicciones en un formato comparable.
- Ser compatibles con el contrato de aplicación aprobado.

Queda prohibido modificar el dataset canónico, el target o los splits desde un pipeline individual.

## Contrato común de experimentación

Cada experimento deberá registrar:

- Identificador del candidato.
- Integrante responsable.
- Versión de datos.
- Features utilizadas.
- Transformaciones.
- Algoritmo.
- Hiperparámetros.
- Semilla.
- Métricas de entrenamiento.
- Métricas de validación.
- Gap de overfitting.
- Matriz de confusión.
- Curva ROC o alternativa cuando aplique.
- Tiempo de entrenamiento.
- Tiempo de inferencia cuando sea relevante.
- Limitaciones y errores observados.
- Resultado de validación cruzada cuando corresponda.

La comparación solo será válida si los cuatro candidatos respetan este contrato.

## Selección del Champion

El equipo seleccionará el pipeline más modelo que se productivizará. Ningún integrante podrá promocionar unilateralmente su candidato.

El Champion deberá:

- Cumplir el overfitting inferior al 5 %.
- Superar una referencia mínima o justificar su selección.
- Mantener un rendimiento aceptable en métricas secundarias.
- Incluir análisis de errores.
- Ser reproducible y serializable.
- Poder cargarse desde la aplicación.
- Mantener el mismo contrato de entrada.
- Tener versión y metadata.

Cuando dos candidatos tengan rendimiento semejante se priorizará, en este orden sujeto a aprobación:

1. Mejor generalización.
2. Menor complejidad operativa.
3. Mayor interpretabilidad.
4. Menor coste de inferencia.

El test final se utilizará una única vez después de la selección y no se reutilizará para tuning.

## Distribución técnica y contratos

### Integrante 1 — Datos y ciclo de vida del dato

- Coordina dataset, carga, EDA, limpieza y contrato de datos.
- Entrena Pipeline A + Modelo A.
- Valida la coherencia entre entrenamiento e inferencia.
- Mantiene validaciones de calidad y referencia de drift cuando corresponda.

### Integrante 2 — Evaluación y ciclo de vida del modelo

- Coordina splits, métricas, overfitting y comparación.
- Entrena Pipeline B + Modelo B.
- Mantiene la tabla de experimentos.
- Coordina selección, análisis de errores y pruebas de regresión.

### Integrante 3 — Frontend y producto

- Define el flujo de usuario y frontend con contratos simulados desde el inicio.
- Entrena Pipeline C + Modelo C.
- Implementa formularios, resultados, errores y feedback visual.
- Prueba la experiencia de usuario y prepara la demostración de negocio.

### Integrante 4 — Backend, integración y despliegue

- Define el servicio de inferencia con contratos simulados desde el inicio.
- Entrena Pipeline D + Modelo D.
- Integra Champion, persistencia, Docker y despliegue.
- Coordina pruebas de API, integración, contenedor y ejecución.

## Contrato de aplicación

Contrato preliminar versionado para que I3 e I4 puedan trabajar con mocks compatibles:

Arquitectura aprobada por I1–I4 en T-0.6:

- I3 — César desarrolla el frontend en `app/frontend/` con React, TypeScript y Vite.
- I4 — Fernanda desarrolla el backend en `app/backend/` con FastAPI, Pydantic y Uvicorn.
- El frontend consume el backend mediante HTTP y JSON; no accede directamente al modelo ni a los datos procesados.
- I4 no modifica `app/frontend/` e I3 no modifica `app/backend/` sin coordinación, para evitar solapamientos.

Ruta de predicción seleccionada:

```text
POST /api/v1/predictions
```

```json
{
  "home_team": "Real Madrid",
  "away_team": "Barcelona",
  "match_date": "2026-10-25"
}
```

Respuesta válida:

```json
{
  "contract_version": "1.0",
  "request_id": "018f0f52-7a6d-7f48-9dcb-58f0e65d21a3",
  "prediction": "H",
  "probabilities": {"H": 0.51, "D": 0.25, "A": 0.24},
  "model_version": "mock-v1",
  "data_version": "laliga_matches_1995_96_to_2025_26_v1",
  "status": "ok",
  "latency_ms": 12.4,
  "message": "Estimación probabilística basada en el histórico disponible."
}
```

Error uniforme:

```json
{
  "status": "error",
  "contract_version": "1.0",
  "request_id": "018f0f52-7a6d-7f48-9dcb-58f0e65d21a3",
  "error": "INVALID_INPUT",
  "message": "El equipo local y el visitante deben ser distintos.",
  "details": [{"field": "away_team", "reason": "SAME_TEAM"}]
}
```

Convenciones:

- Fecha ISO-8601 `YYYY-MM-DD`.
- `home_team` y `away_team` son obligatorios, se recortan en los extremos y admiten entre 1 y 80 caracteres.
- Los equipos deben ser distintos sin diferenciar mayúsculas y deben existir en el catálogo disponible.
- No se admiten campos adicionales ni cuerpos JSON mayores de 4 KiB.
- Para `match_date`, el backend solo usa partidos estrictamente anteriores; si no existe historial suficiente devuelve un error controlado.
- `prediction` solo admite `H`, `D` o `A`.
- El backend calcula las features; el frontend no envía agregados históricos ni transforma datos.
- Las probabilidades se devuelven para las tres clases y suman 1 con tolerancia numérica.
- `latency_ms` mide el procesamiento dentro del backend; el objetivo caliente es p95 menor de 1 segundo, sin contar red ni arranque en frío.
- Los logs incluyen `request_id`, ruta, estado, latencia y versiones, pero no almacenan el payload completo.
- El mecanismo de feedback se añade sin romper este contrato si se alcanza el Nivel Medio.

### Códigos HTTP y errores

| HTTP | Código de error | Uso |
|---:|---|---|
| `200` | — | Predicción válida. |
| `400` | `MALFORMED_JSON` | El cuerpo no es JSON válido. |
| `404` | `TEAM_NOT_FOUND` | Algún equipo no pertenece al catálogo. |
| `409` | `INSUFFICIENT_HISTORY` | No existe historial anterior suficiente. |
| `413` | `PAYLOAD_TOO_LARGE` | El cuerpo supera 4 KiB. |
| `415` | `UNSUPPORTED_MEDIA_TYPE` | El contenido no es JSON. |
| `422` | `INVALID_INPUT` | Faltan o sobran campos, la fecha es inválida o los equipos coinciden. |
| `500` | `INTERNAL_ERROR` | Fallo inesperado sin exponer trazas al cliente. |
| `503` | `MODEL_UNAVAILABLE` | El mock o el Champion no están disponibles. |

Todos los errores utilizan el sobre uniforme mostrado arriba. `details` puede ser una lista vacía y nunca expone trazas, secretos, rutas locales o datos del dataset.

### Versionado y compatibilidad

- La versión mayor forma parte de la ruta: `/api/v1`.
- `contract_version` identifica la revisión compatible del contrato v1.
- Añadir un campo opcional es compatible; eliminar, renombrar o cambiar el significado de un campo requiere `/api/v2`.
- `model_version` y `data_version` evolucionan de forma independiente y no cambian por sí solas la versión de la API.
- Sustituir `mock-v1` por el Champion no modifica la ruta ni el formato consumido por el frontend.

El frontend no realizará transformaciones estadísticas propias del pipeline.

## Requisitos no funcionales

| ID | Requisito | Objetivo |
|---|---|---|
| RNF-01 | Reproducibilidad | Un clon limpio reproduce preparación, evaluación y tests con comandos documentados. |
| RNF-02 | Latencia de inferencia | Objetivo inicial p95 < 1 s, medido sin incluir arranque en frío. |
| RNF-03 | Calidad de respuesta | Ninguna entrada inválida produce excepción no controlada. |
| RNF-04 | Seguridad | Secretos fuera de Git y logs; dependencias con versiones registradas. |
| RNF-05 | Portabilidad | Compatibilidad Docker comprobada temprano; gate formal de contenedor en Nivel Avanzado. |
| RNF-06 | Observabilidad mínima | Logs estructurados con versión del modelo, estado y latencia, sin datos sensibles. |

## Testing distribuido

- Integrante 1: tests de carga, contrato de datos y transformaciones comunes.
- Integrante 2: tests de métricas, overfitting, comparación y regresión.
- Integrante 3: tests de interfaz y flujo de usuario.
- Integrante 4: tests de backend, integración, serialización, Docker y despliegue.

Cada integrante probará además su pipeline y modelo candidato. El autor de un componente no será su único revisor.

## Definición de terminado

Una tarea solo se considerará terminada cuando:

- Cumpla sus dependencias.
- Respete los contratos de esta especificación.
- Tenga código o documento completo.
- Tenga pruebas proporcionales al riesgo.
- Registre comandos y resultados de verificación.
- Actualice la documentación afectada.
- No rompa el Nivel Esencial.
- Tenga la revisión cruzada indicada en `4_tasks.md`.
- Disponga de evidencia reproducible.

## Seguridad y privacidad

- No se guardarán secretos en Git.
- No se registrarán credenciales en logs.
- No se utilizarán datos personales sensibles sin necesidad y justificación.
- Las predicciones no se presentarán como certezas.
- La importancia de variables no se presentará como causalidad.
- Un sistema de drift nunca promoverá por sí solo un modelo.

## Control de cambios

Cambios sobre dataset, target, limpieza, splits, métricas, overfitting, contratos o arquitectura requieren:

1. Propuesta explícita.
2. Revisión de las personas afectadas.
3. Aprobación del equipo.
4. Actualización de `.specify/`.
5. Reevaluación de candidatos si se pierde comparabilidad.
6. Si cambia la limpieza o el dataset procesado, ejecutar de nuevo `scripts/run_laliga_preprocessing.py`, `python -m src.evaluation.splits` y `verify_preprocessing_split_contract`; registrar la nueva huella, cobertura de `match_id` y conteos antes de permitir cualquier entrenamiento.

## Trazabilidad mínima

| Requisito o decisión | Tareas principales | Evidencia esperada |
|---|---|---|
| DEC-01–DEC-06 | T-0.2a, T-0.2b, T-0.3 | ADR, procedencia, licencia y acta de decisión |
| DEC-07–DEC-09 | T-0.4, T-1.5 | contrato de evaluación, splits versionados y tests |
| RF-01–RF-06 | T-0.6, T-1.6, T-1.7, T-3.2, T-3.3 | fixtures de contrato, tests de API/UI y smoke test |
| ML-01 Datos sin leakage | T-1.1–T-1.5 | manifest, diccionario, generador de features y test temporal |
| ML-02 Cuatro candidatos | T-2.1–T-2.5 | registros de experimentos comparables |
| ML-03 Champion | T-2.6, T-3.1 | decisión, artefacto, metadata y evaluación final |
| RNF-01–RNF-06 | T-3.4, T-3.6, T-5.1–T-5.4 | comandos, resultados, logs, contenedor y despliegue |

## Estado del documento

| Campo | Valor |
|---|---|
| Estado | v1.0 — T-0.2b, T-0.4, T-0.5, T-0.6 y T-1.5 ratificados el 2026-07-24 |
| Fecha | 24/07/2026 |
| Bloqueos | T-1.4a y T-1.6–T-1.7 antes de `Data Ready` |
