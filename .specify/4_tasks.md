# SPEC 4 — Backlog de tareas

## Protocolo de ejecución

Antes de comenzar una tarea:

1. Leer completamente `.specify/`.
2. Confirmar que las dependencias están satisfechas.
3. Confirmar responsable, revisor, requisitos y archivos afectados.
4. Usar la estrategia Git aprobada.
5. No ampliar el alcance sin actualizar la tarea.

Antes de marcarla como terminada:

1. Ejecutar la verificación indicada.
2. Registrar la evidencia.
3. Actualizar documentación afectada.
4. Obtener la revisión cruzada.
5. Confirmar que no se rompe el Nivel Esencial.

Toda tarea nueva deberá incluir, cuando aplique: IDs `RF/ML/RNF/DEC`, archivos afectados, comando de verificación y ruta de evidencia. Un adelanto solo es válido si se identifica como **spike exploratorio autorizado**.

## Estados

- `[ ]`: pendiente.
- `[~]`: en progreso.
- `[x]`: completada y verificada.
- `[!]`: bloqueada.
- `[-]`: cancelada o no aplica.

## Roles

- I1 — Arnaldo: Datos y ciclo de vida del dato + Pipeline A + Modelo A.
- I2 — Johans: Evaluación y ciclo de vida del modelo + Pipeline B + Modelo B.
- I3 — César: Frontend y producto + Pipeline C + Modelo C.
- I4 — Fernanda: Backend, integración y despliegue + Pipeline D + Modelo D.

## Tablero de gates

| Gate | Estado | Bloqueo o evidencia principal |
|---|---|---|
| Alineación | Cerrado | T-0.1: SDD reconciliado y aprobado por I1–I4 |
| Dataset técnico | Cerrado | Daily 22/07, ADR-0001, loader y manifest |
| Licencia | Cerrado | T-0.2b: ratificado por el equipo en daily 2026-07-24; uso local aceptado, incluida la permanencia de los CSV ya trackeados en Git. Reafirmado 2026-07-30: el repositorio es público en GitHub (se despliega desde `develop`), por lo que esa ratificación cubre explícitamente el riesgo de redistribución pública, no solo "uso local". Ver `docs/data_acquisition.md` y `team_risk_acceptance` en `src/data/laliga_loader.py` |
| Evaluación | Cerrado | T-0.4/T-1.5: métrica, gap, ventanas temporales y particiones ratificados por el equipo en daily 2026-07-24 |
| Candidatos | Cerrado | T-0.5: cuatro algoritmos asignados, ver `docs/decisions/0003-four-candidate-models.md` |
| Aplicación | Cerrado | T-0.6: arquitectura y contrato aprobados por I1–I4 |
| `Data Ready` | Cerrado | T-1.8: checklist de `2_spec.md` completada 2026-07-26 |
| Nivel Esencial | Cerrado | T-3.7: gate de `3_plan.md` satisfecho 2026-07-26, Champion D integrado y 28 tests aprobados |

## Fase 0 — Decisiones bloqueantes

### [x] T-0.1 Revisar y aprobar `.specify/`

- Responsable: todo el equipo.
- Revisor: todo el equipo.
- Dependencias: ninguna.
- Requisitos: todos los `DEC`.
- Acción: leer `0_constitution.md` y los cuatro documentos SPEC, registrar dudas y aprobar o corregir el contrato.
- Criterio de aceptación: los cuatro integrantes aprueban dominio, gates, flujo común de datos, contratos y cuatro pipelines.
- Evidencia: aprobación fechada en daily o PR.
- Reconciliación 2026-07-24: la fuente de verdad para T-0.4 fija las ventanas canónicas en `2_spec.md`: train 1995-96–2019-20, validación 2020-21–2022-23 y test protegido 2023-24–2025-26. La propuesta alternativa queda retirada. T-0.4 permanece en progreso hasta la ratificación individual; una confirmación de representante no permite cerrarla.
- Cierre 2026-07-24: aprobación y visto bueno explícitos de I1 Arnaldo `[x]`, I2 Johans `[x]`, I3 César `[x]` e I4 Fernanda `[x]`. Evidencia: confirmación conjunta del equipo registrada en la daily 24/07/2026. Se cumplen el criterio de aceptación y la revisión cruzada.

### [x] T-0.2a Evaluar y seleccionar técnicamente el dataset

- Responsable: I1, con aportes de I2, I3 e I4.
- Dependencias: ninguna; spike de decisión previo al SDD definitivo.
- Requisitos: DEC-01, DEC-03–DEC-06.
- Acción: evaluar target, tamaño, leakage, interpretabilidad, balance y viabilidad de aplicación.
- Criterio de aceptación: selección técnica, unidad partido, usuario y target explicables.
- Evidencia: daily 22/07/2026, `docs/decisions/0001-laliga-dataset-target-proposal.md`, EDA y manifest.

### [x] T-0.2b Verificar condiciones de uso y redistribución del dataset

- Prioridad: **P0 — bloqueante para `Data Ready`**.
- Responsable: I1.
- Revisores: I2, I3 e I4.
- Dependencias: T-0.2a.
- Requisitos: DEC-01, DEC-02 y RNF-01.
- Acción: verificar para `LaLiga_Matches.csv` y `laliga_2025_2026_stats.csv` la fuente original, autor o entidad responsable, condiciones de uso, permiso de redistribución y compatibilidad con un repositorio público. Registrar URL, fecha de consulta y evidencia verificable; distinguir acceso gratuito de licencia abierta.
- Criterio de aceptación: cada fuente tiene procedencia y condiciones documentadas y una decisión explícita de conservación y redistribución para sus copias raw y derivadas. La adquisición reproducible y la política de uso quedan registradas antes de cerrar el gate.
- Verificación: contrastar `reports/metrics/source_provenance.json`, las fuentes publicadas y los archivos versionados mediante `git ls-files data/raw data/processed`.
- Evidencia: `reports/metrics/source_provenance.json`, `reports/metrics/redistribution_remediation.json`, `docs/decisions/0001-laliga-dataset-target-proposal.md` y GitHub issue #41.
- Apertura 2026-07-23: tarea formalizada como prioridad inmediata en GitHub issue #41, asignada a I1, añadida a `Proyecto6-Grupo4`, con prioridad `Urgent` y estado `In progress`. La procedencia técnica está identificada, pero no consta una licencia abierta explícita para ambas fuentes ni la aprobación del equipo sobre redistribución. Hasta resolverlo, `T-1.1` y `T-1.8` no pueden cerrarse.
- Revisión I1 2026-07-23: la ficha de Kaggle declara `Data files © Original Authors`; Football-Data ofrece descarga gratuita y declara la finalidad de predicción de partidos, pero ninguna fuente publica una licencia abierta o una autorización explícita para redistribuir los archivos. Decisión I1: uso local para el proyecto compatible con la finalidad indicada; publicación de raw y derivados fila a fila **no autorizada mientras no exista permiso escrito**.
- Estado tras revisión I1: resultado y verificación 15/15 publicados en el issue #41; ocho comprobaciones completadas y estado del Project cambiado a `In review`. El issue permanece abierto y la aprobación I2/I3/I4 continúa sin marcar.
- Decisión de conservación 2026-07-24: los CSV raw y los derivados fila a fila se mantienen dentro del directorio de trabajo para ejecución local y reproducibilidad. Esta decisión **no autoriza** su redistribución pública: mientras no exista permiso escrito, los datos solo pueden mantenerse en una copia local o en un repositorio privado con acceso controlado. Antes de cualquier publicación o cambio de visibilidad se debe adjuntar el permiso explícito de ambas fuentes o retirar los archivos.
- Cierre 2026-07-24: ratificado por el equipo en daily. Misma salvedad que T-0.3/T-0.4: confirmación de representante del equipo en esta sesión, no firma individual archivada de cada integrante; si algún integrante objeta, debe reabrirse. El equipo revisó que `LaLiga_Matches.csv`, `laliga_2025_2026_stats.csv` y `laliga_matches_clean.csv` siguen trackeados en el historial de Git y decidió explícitamente aceptar esa situación sin remediación adicional; no queda ninguna acción pendiente sobre este punto.

### [x] T-0.3 Definir problema, usuarios y target

- Responsable: todo el equipo; coordina I1.
- Dependencias: T-0.2a.
- Requisitos: DEC-03–DEC-06.
- Acción: aprobar problema de negocio, usuario, unidad de predicción, target y clases.
- Criterio de aceptación: el equipo puede explicar qué se predice, para quién y con qué utilidad.
- Evidencia: `1_intent.md` y `2_spec.md` actualizados.
- Avance 2026-07-22: propuesta prepartido y target multiclase `result_ft` documentados. Pendiente aprobación de todo el equipo.
- Cierre 2026-07-23: confirmada en sesión de trabajo para desbloquear T-0.4. Queda registrado que la confirmación se recibió de un representante del equipo, no como firma individual de cada integrante; si algún integrante objeta, debe reabrirse.

### [x] T-0.4 Definir protocolo de evaluación

- Responsable: I2.
- Revisor: I1.
- Dependencias: T-0.3.
- Requisitos: DEC-07–DEC-09, ML-03, ML-04, ML-06.
- Acción: aprobar macro-F1 o alternativa justificada, métricas secundarias, ventanas temporales, baselines, semilla algorítmica y fórmula de overfitting.
- Criterio de aceptación: protocolo aprobado por los cuatro integrantes.
- Evidencia: contrato registrado en `2_spec.md`.
- Avance 2026-07-23: propuesta registrada — métrica principal `macro-F1`, secundarias (accuracy, balanced accuracy, precisión/recall/F1 por clase, log loss, matriz de confusión), fórmula de overfitting (`gap < 0.05` sobre `macro-F1` train/validación) y partición cronológica por temporada con semilla `42`. Detalle y justificación en `docs/decisions/0002-evaluation-protocol-proposal.md`.
- Cierre 2026-07-24: I1, I2, I3 e I4 aprueban el contrato, incluidas métricas, gap, semilla y ventanas canónicas. Evidencia: confirmación conjunta del equipo registrada en la daily 24/07/2026 y acta de T-0.1.

### [x] T-0.5 Elegir cuatro modelos candidatos

- Responsable: todo el equipo; coordina I2.
- Dependencias: T-0.3, T-0.4.
- Requisito: ML-02.
- Acción: asignar un algoritmo a cada integrante y justificar diversidad y viabilidad.
- Criterio de aceptación: candidatos A, B, C y D registrados sin duplicación injustificada.
- Evidencia: tabla de decisiones de `2_spec.md` actualizada.
- Cierre 2026-07-24: confirmado por el equipo (representante de sesión). Candidato A (I1): regresión logística multinomial. Candidato B (I2): gradient boosting (HistGradientBoostingClassifier/XGBoost/LightGBM). Candidato C (I3): random forest. Candidato D (I4): SVM con kernel RBF y probabilidades. Diversidad cubierta: lineal, boosting de árboles, bagging de árboles y margen. Detalle y justificación en `docs/decisions/0003-four-candidate-models.md`.

### [x] T-0.6 Definir aplicación y contratos preliminares

- Responsable: I3 e I4.
- Revisores: I1 e I2.
- Dependencias: T-0.3.
- Requisitos: RF-01–RF-06, RNF-02–RNF-06.
- Acción: aprobar tecnología, separación lógica o física, endpoints, entrada, salida, errores, latencia y versionado.
- Criterio de aceptación: frontend y backend pueden avanzar con mocks compatibles.
- Evidencia actual: contrato JSON preliminar, tecnologías, arquitectura y ruta registrados en `2_spec.md`.
- Avance 2026-07-24: I3/I4 seleccionan frontend React + TypeScript con Vite y backend FastAPI + Pydantic servido con Uvicorn, en procesos separados comunicados mediante HTTP/JSON. La ruta de predicción será `POST /api/v1/predictions`. César conserva la propiedad exclusiva de `app/frontend/` y Fernanda la de `app/backend/` para evitar solapamientos.
- Contrato listo para revisión 2026-07-24: definidos códigos HTTP, error uniforme, límites de entrada, objetivo de latencia p95, observabilidad mínima y reglas de versionado/compatibilidad en `2_spec.md`.
- Cierre 2026-07-24: I1 e I2 confirmaron su aprobación del contrato preparado por I3/I4. Quedan aprobadas las tecnologías, la arquitectura separada, la ruta versionada, los esquemas JSON, los errores, los límites, la latencia y el versionado. La implementación y sus fixtures corresponden a T-1.6/T-1.7.
- Revisión 2026-07-29: la implementación final de `app/frontend/` no usa React, TypeScript ni Vite (no hay `package.json` ni build); es HTML + CSS + JavaScript plano servido como estático por FastAPI/nginx. El resto del contrato de T-0.6 (separación frontend/backend, ruta `POST /api/v1/predictions`, esquemas y errores) se cumplió tal cual se aprobó.

### [x] T-0.7 Definir estrategia Git

- Responsable: todo el equipo.
- Dependencias: ninguna; decisión de bootstrap.
- Acción: acordar ramas, PR, revisiones y commits.
- Criterio de aceptación: existen rama de integración y cuatro ramas iniciales; el flujo está documentado.
- Evidencia: estrategia registrada en `2_spec.md`, estructura inicial y ramas publicadas en GitHub.

### [x] T-0.8 Elegir herramienta organizativa

- Responsable: todo el equipo.
- Dependencias: ninguna; decisión de bootstrap.
- Acción: elegir herramienta, crear el tablero y registrar su referencia.
- Criterio de aceptación: backlog visible y estados de trabajo acordados.
- Evidencia: GitHub Project `Proyecto6-Grupo4`, issues #3–#35 y daily 22/07/2026.

## Fase 1 — Base común y `Data Ready`

### [x] T-1.1 Implementar conexión única al dataset

- Responsable: I1.
- Revisor: I4.
- Dependencias para iniciar spike: T-0.2a, T-0.3.
- Dependencia para completar: T-0.2b.
- Requisitos: DEC-01, DEC-02, ML-01, RNF-01.
- Acción: crear un mecanismo reproducible para cargar el dataset canónico sin modificar el original.
- Criterio de aceptación: los cuatro integrantes pueden obtener la misma versión de datos.
- Verificación: comprobar schema, dimensiones y huella o versión.
- Evidencia provisional: `src/data/laliga_loader.py`, `scripts/run_laliga_preprocessing.py`, `reports/metrics/dataset_manifest.json`, `reports/metrics/source_provenance.json` y tests unitarios. Pendiente revisión de I4 y cierre de dependencias.
- Cierre técnico I1 2026-07-24: regenerados desde raw el dataset canónico y su manifest; contrato validado con 11.944 filas, 54 columnas, SHA-256 `6288a872df07a196a48ea05039671feba0616489927ebc12b344d96f0e921b0c`, 0 IDs duplicados y 0 targets nulos. Preparado para revisión de I4.
- Reverificación 2026-07-24: `scripts/run_laliga_preprocessing.py` regeneró el dataset canónico con 11.944 filas, 54 columnas, 100 solapamientos resueltos, 0 `match_id` duplicados, 0 targets nulos y SHA-256 `6288a872df07a196a48ea05039671feba0616489927ebc12b344d96f0e921b0c`. Suite completa: 16/16 pruebas aprobadas. Pendiente únicamente la revisión cruzada de I4.
- Revisión cruzada I4 2026-07-24: revisados `load_raw_sources`, el contrato de `load_processed_dataset`, la regeneración mediante `scripts/run_laliga_preprocessing.py` y el manifest. Se corrigió el estado de procedencia para reflejar la decisión T-0.2b: uso local o repositorio privado, sin autorización de redistribución pública. Verificación reproducida: 11.944 filas, 54 columnas, SHA-256 canónico y 16/16 pruebas aprobadas. T-1.1 aceptada.

### [x] T-1.2 Crear diccionario y auditoría de datos

- Responsable: I1.
- Revisor: I3.
- Dependencias: T-1.1.
- Requisito: ML-01.
- Acción: documentar columnas, tipos, target, identificadores, disponibilidad y riesgos.
- Criterio de aceptación: todas las variables tienen rol y descripción.
- Evidencia: diccionario de datos revisado.
- Evidencia provisional: `reports/metrics/data_dictionary.csv`, `reports/metrics/missingness.csv` y `reports/metrics/eda_summary.json`. Pendiente revisión de I3.
- Cierre técnico I1 2026-07-24: diccionario regenerado para las 54 columnas, con tipo, rol, disponibilidad, tratamiento de nulos y riesgo de leakage. La evidencia queda lista para revisión de I3.
- Revisión cruzada I3 2026-07-24: revisados el diccionario de las 54 columnas, la auditoría de nulos y el resumen EDA. Se confirma `result_ft` como target, `match_id` como identificador sin papel predictivo, la exclusión de variables posteriores al evento y metadatos de fuente, y el riesgo temporal de las cuotas de cierre. Los 29 campos estructuralmente vacíos del alcance de desarrollo quedan documentados para no imputarlos. Verificación reproducida: `./.venv/Scripts/python.exe -m pytest -q` (**16 passed**). T-1.2 aceptada.

### [x] T-1.3 Realizar EDA compartido

- Responsable: todos; coordina I1.
- Dependencias: T-1.1, T-1.2.
- Requisitos: ML-01, ML-06.
- Acción: dividir preguntas de análisis entre los cuatro y consolidar un único EDA.
- Criterio de aceptación: nulos, duplicados, distribuciones, target, relaciones, correlaciones y leakage analizados.
- Evidencia: notebook o informe reproducible con interpretaciones.
- Evidencia provisional: `notebooks/01_laliga_eda.ipynb`, `reports/laliga_eda.md` y once figuras persistentes en `reports/figures/`, incluidas outliers y dos matrices de confusión descriptivas. Análisis técnico completo; pendiente revisión cruzada de los cuatro integrantes.
- Cierre técnico I1 2026-07-24: EDA regenerado con 11 figuras, auditoría de nulos/duplicados/target, análisis temporal, outliers, baseline descriptivo y matriz de leakage. El EDA usa exclusivamente train+validación (10.804 filas); el test 2023-24–2025-26 queda excluido. Verificación registrada en `reports/metrics/eda_verification.md`; pendiente revisión cruzada humana.
- Revisión compartida I1–I4 2026-07-24: el equipo revisó el notebook, informe, métricas y las 11 figuras. Confirma que el EDA analiza nulos, duplicados, distribuciones, desbalance del target, relaciones, correlaciones descriptivas, outliers e indicadores de leakage; que las dos matrices son baselines descriptivas y no candidatos; y que el test protegido queda fuera de todo cálculo y visualización. Verificación reproducida: preprocesamiento y splits regenerados con SHA-256 `6288a872df07a196a48ea05039671feba0616489927ebc12b344d96f0e921b0c`, 11.944 IDs cubiertos una vez y suite **16 passed**. T-1.3 aceptada.
- Reverificación I4 2026-07-24: confirmado el alcance exclusivo de train+validación (10.804 filas) y corregidas las referencias desactualizadas a 2025-26 y a la ausencia de splits. El informe regenerado identifica 2025-26 como test protegido, evita interpretar una baseline de cuotas sin observaciones y reconoce las particiones congeladas. Suite completa: **16 passed**.

### [x] T-1.4 Implementar limpieza común

- Responsable: I1.
- Revisores: I2 e I4.
- Dependencias: T-1.3.
- Requisito: ML-01.
- Acción: codificar las reglas aprobadas sin alterar el dataset original.
- Criterio de aceptación: limpieza determinista, documentada y probada.
- Evidencia: tests y comparación antes/después.
- Evidencia provisional 2026-07-23: `notebooks/00_laliga_preprocessing.ipynb`, `data/processed/laliga_matches_clean.csv`, `reports/metrics/preprocessing_summary.json`, `reports/metrics/source_column_policy.csv` y pruebas unitarias/integración. Pendientes revisión de I2/I4 y cierre de dependencias.
- Revisión I2 2026-07-23: dataset limpio auditado sin duplicados, targets nulos ni incoherencias marcador/resultado; `load_processed_dataset` valida el contrato de tipos y la suite de tests pasa (14/14). Aceptable como base para congelar particiones (T-1.5). Revisión de I4 sigue pendiente.
- Cierre técnico I1 2026-07-24: limpieza determinista regenerada sin modificar raw, con política de columnas, reporte antes/después y 0 incoherencias marcador/target. Se añadió `verify_preprocessing_split_contract` para asegurar que dataset, `match_id`, huella y conteos coinciden con las particiones congeladas; 15/15 pruebas en verde. Todo cambio de limpieza obliga a regenerar preprocesamiento, splits y esta verificación antes de entrenar. Pendiente revisión de I4.
- Revisión cruzada I4 2026-07-24: revisados `preprocess_sources`, la política de columnas, `load_processed_dataset` y el contrato con los splits. Se confirma que los CSV raw no se modifican, que la deduplicación con prioridad de fuente detallada resuelve 100 solapamientos y que la limpieza conserva 2 nulos opcionales de descanso sin imputarlos. Regeneración reproducida: 11.944 filas, 54 columnas, 0 IDs duplicados, 0 targets nulos, 0 incoherencias marcador/target y SHA-256 `6288a872df07a196a48ea05039671feba0616489927ebc12b344d96f0e921b0c`; `verify_preprocessing_split_contract` valida 9.607/1.197/1.140 y la suite queda en **16 passed**. T-1.4 aceptada.

### [x] T-1.4a Implementar generador común de features históricas sin leakage

- Prioridad: **P0 — bloqueante para `Data Ready`**.
- Responsable: I1.
- Revisor: I2.
- Dependencias: T-1.4, T-1.5.
- Requisitos: ML-01, ML-06.
- Acción: implementar y documentar un generador común de features históricas para los cuatro candidatos. Debe recorrer los partidos en orden cronológico estable y producir forma, fuerza, goles, puntos, Elo o enfrentamientos únicamente a partir de encuentros estrictamente anteriores; toda ventana o agregación debe aplicar `shift(1)` o un mecanismo equivalente. No puede incluir columnas posteriores al evento, `match_id`, metadatos de cobertura ni usar el target del partido actual.
- Criterio de aceptación: el generador es determinista, versionado y reutilizable por los cuatro pipelines; su schema, parámetros y origen de datos quedan documentados. Ningún resultado futuro modifica las features de partidos anteriores y las transformaciones ajustables se estiman solo en train. El test permanece protegido: no se usa para ajuste, selección ni cálculo de parámetros.
- Verificación: ejecutar el generador sobre el dataset y splits congelados; comprobar schema, `match_id`, SHA-256 y conteos. Añadir pruebas unitarias de orden temporal, `shift(1)`, empate de fechas y no-leakage al alterar un resultado futuro, más una prueba de integración reproducible. Ejecutar `./.venv/Scripts/python.exe -m pytest -q`.
- Evidencia esperada: implementación en `src/data/`, pruebas en `tests/unit/` y `tests/integration/`, manifest de features en `reports/metrics/` y contrato actualizado en `2_spec.md`.
- Cierre 2026-07-26: revisión de I2 confirmada. `historical_features_v1` se regeneró con SHA `563634a…d8f8d2c81`, conserva 11.944 IDs y los conteos 9.607/1.197/1.140. Las pruebas cubren cold-start, orden estable, empates de fecha, equivalencia a `shift(1)` y mutación futura sin leakage.

### [x] T-1.5 Congelar particiones comunes

- Responsables: I1 e I2.
- Revisores: I3 e I4.
- Dependencias: T-1.4, T-0.4.
- Acción: generar y versionar train, validación y test mediante el protocolo aprobado.
- Criterio de aceptación: los cuatro candidatos reciben los mismos registros.
- Evidencia: índices, metadata o función reproducible; test final protegido.
- Avance 2026-07-23: implementado `src/evaluation/splits.py` (partición cronológica por temporada, congelada como constante, sin aleatoriedad ni estratificación). Genera `data/processed/splits/laliga_splits.csv` (match_id, season, split) y `reports/metrics/split_manifest.json` (protocolo, semilla 42, conteos y fracciones). Resultado: train 9.607 filas (1995-96–2019-20), validación 1.197 filas (2020-21–2022-23), test 1.140 filas (2023-24–2025-26, protegido). Falla explícitamente si aparece una temporada no contemplada, en vez de reasignar en silencio. Pruebas: `tests/unit/test_splits.py` (5 casos), suite completa 14/14 en verde. Pendiente revisión de I1.
- Aprobación técnica I1 2026-07-23: verificados el SHA-256 del dataset canónico, la asignación cronológica, la regeneración local de 11.944 índices sin IDs duplicados o ausentes, los conteos 9.607/1.197/1.140 y la protección del test. Suite completa: 14/14 pruebas aprobadas. La asignación queda versionada mediante la constante y el manifest; el CSV regenerable permanece excluido por la política general de `data/processed/*`.
- Cierre 2026-07-24: revisión cruzada de I3 e I4 confirmada por el equipo en daily. Misma salvedad que otras confirmaciones de representante: si I3 o I4 objetan al ver el detalle, la tarea se reabre.
- Regla acordada 2026-07-24: cualquier cambio en las reglas de limpieza de T-1.4 (o en los CSV raw) invalida el SHA-256 registrado y obliga a reejecutar `scripts/run_laliga_preprocessing.py` + `python -m src.evaluation.splits`, reconfirmando hash, 11.944 `match_id`, cortes por temporada y conteos 9.607/1.197/1.140 antes de que T-1.5 siga vigente. Detalle en `docs/decisions/0002-evaluation-protocol-proposal.md`.
- Reverificación 2026-07-24: reejecutados `scripts/run_laliga_preprocessing.py` y `python -m src.evaluation.splits`. SHA-256 idéntico (`6288a872df07a196a48ea05039671feba0616489927ebc12b344d96f0e921b0c`), 11.944 filas y 11.944 `match_id` únicos, mismos cortes por temporada (train 1995-96–2019-20, validación 2020-21–2022-23, test 2023-24–2025-26) y mismos conteos 9.607/1.197/1.140. Suite completa 15/15 en verde. Pendiente como criterio permanente de revisión en T-2.1–T-2.4: ningún pipeline debe leer filas `split == "test"` salvo en T-2.6.

### [x] T-1.6 Crear frontend simulado

- Responsable: I3.
- Revisor: I4.
- Dependencias: T-0.6, T-1.2.
- Requisitos: RF-01, RF-03–RF-06.
- Acción: implementar o diseñar el flujo con respuestas mock según la arquitectura aprobada.
- Criterio de aceptación: formulario, resultado y error pueden demostrarse sin modelo definitivo.
- Evidencia: prueba visual o test de interfaz.
- Cierre 2026-07-26: integrado el formulario y visualización desde `app/frontend/public/`; posteriormente conectado al contrato real de `/api/v1/predictions` en T-3.3.

### [x] T-1.7 Crear backend de inferencia simulado

- Responsable: I4.
- Revisor: I3.
- Dependencias: T-0.6, T-1.2.
- Requisitos: RF-01–RF-06, RNF-02–RNF-06.
- Acción: implementar el contrato mock con `home_team`, `away_team` y `match_date`; devolver `H/D/A`, probabilidades, versiones, latencia y errores uniformes.
- Criterio de aceptación: contrato consumible por frontend.
- Verificación: fixtures válidos e inválidos compartidos con I3.
- Evidencia: prueba de contrato o llamada reproducible, comandos y resultados.
- Cierre 2026-07-26: contrato implementado en FastAPI con validación Pydantic, respuestas y errores uniformes; sustituido por el Champion real sin cambiar ruta ni formato en T-3.2. Prueba de API incluida en la suite.

### [x] T-1.8 / T-1.INT Verificar gate `Data Ready`

- Responsable: todo el equipo; coordina I2.
- Dependencias: T-0.1, T-0.2b, T-0.4, T-0.5, T-1.1 a T-1.7 y T-1.4a.
- Acción: completar la checklist de `2_spec.md`.
- Criterio de aceptación: no quedan decisiones de datos, evaluación o candidatos que bloqueen el entrenamiento.
- Evidencia: checklist completada y revisión cruzada.
- Cierre 2026-07-26: checklist de `2_spec.md` completa, T-1.4a revisada por I2 y mocks integrados. El manifest de datos, splits y features queda fijado antes de los cuatro entrenamientos.

## Fase 2 — Cuatro candidatos en paralelo

### [x] T-2.1 Desarrollar Pipeline A + Modelo A

- Responsable: I1.
- Revisor: I2.
- Dependencias: T-1.8.
- Acción: crear, entrenar, evaluar, serializar y documentar el candidato A.
- Criterio de aceptación: cumple el contrato común de experimentación.
- Evidencia: pipeline, artefacto, métricas, tests y registro.
- Cierre 2026-07-26: revisión de I2 confirmada. Métrica de validation macro-F1 0,464836, gap 0,000000; evidencia y matriz en `reports/experiments/`.

### [x] T-2.2 Desarrollar Pipeline B + Modelo B

- Responsable: I2.
- Revisor: I3.
- Dependencias: T-1.8.
- Acción: crear, entrenar, evaluar, serializar y documentar el candidato B.
- Criterio de aceptación: cumple el contrato común de experimentación.
- Evidencia: pipeline, artefacto, métricas, tests y registro.
- Cierre técnico 2026-07-26: `HistGradientBoostingClassifier` bajo el contrato común; queda descartado por gap 0,376171.

### [x] T-2.3 Desarrollar Pipeline C + Modelo C

- Responsable: I3.
- Revisor: I4.
- Dependencias: T-1.8.
- Acción: crear, entrenar, evaluar, serializar y documentar el candidato C sin abandonar el frente de frontend.
- Criterio de aceptación: cumple el contrato común de experimentación y el frontend sigue integrable.
- Evidencia: pipeline, artefacto, métricas, tests y registro.
- Cierre técnico 2026-07-26: `RandomForestClassifier` bajo el contrato común; queda descartado por gap 0,261803.

### [x] T-2.4 Desarrollar Pipeline D + Modelo D

- Responsable: I4.
- Revisor: I1.
- Dependencias: T-1.8.
- Acción: crear, entrenar, evaluar, serializar y documentar el candidato D sin abandonar el frente de backend.
- Criterio de aceptación: cumple el contrato común de experimentación y el backend sigue integrable.
- Evidencia: pipeline, artefacto, métricas, tests y registro.
- Cierre de revisión I1 2026-07-26: entrega `SVC(kernel="rbf", probability=True)` reproducible, sin test en entrenamiento, con escalado ajustado en train, serialización, test unitario y registro. Validation macro-F1 0,483744; gap 0,009166.

### [x] T-2.5 Consolidar tabla de experimentos

- Responsable: I2.
- Revisores: I1, I3 e I4.
- Dependencias: T-2.1 a T-2.4.
- Acción: verificar comparabilidad y registrar resultados de los cuatro candidatos.
- Criterio de aceptación: ninguna comparación usa datos, métricas o reglas diferentes sin explicarlo.
- Evidencia: tabla completa y observaciones de calidad.
- Cierre 2026-07-26: tabla completa A–D con mismo SHA de datos, manifest de split y versión/hash de features. A y D cumplen gap; B y C quedan descalificados por sobreajuste.

### [x] T-2.6 Seleccionar y versionar Champion

- Responsable: todo el equipo; coordina I2.
- Dependencias: T-2.5.
- Requisitos: ML-03–ML-05.
- Acción: seleccionar con validación, congelar la decisión y solo después evaluar una vez el test final.
- Criterio de aceptación: Champion cumple overfitting, integración y métricas aprobadas.
- Evidencia: decisión, metadata, métricas finales y artefacto completo.
- Cierre 2026-07-26: seleccionado D por macro-F1 de validation 0,483744 y gap 0,009166. Reentrenado en train+validation (10.804 filas) y evaluado una vez en test (1.140): macro-F1 0,470529. Metadata en `reports/experiments/champion_metadata.json`.
- Actualización 2026-07-28 (I2), Champion reemplazado por el ensemble: a petición explícita del equipo (ver enmienda 2026-07-28 en `docs/decisions/0003-four-candidate-models.md`), `scripts/select_champion.py` se amplió para incluir `reports/experiments/ensemble_abcd_metrics.json` (mismo esquema que A-D, generado por `train_candidate`) en la comparación. Nuevo Champion: **`ENSEMBLE_ABCD`** (votación suave de A, B retunado, C regularizado y D calibrado). Validation macro-F1 0,488281, gap 0,003112 — el mejor de toda la tabla. Reentrenado en train+validation y evaluado en test (tercera evaluación de test para el linaje de Champion; ver nota de gobernanza en T-4.2): macro-F1 test 0,479580, mejora real sobre el 0,470529 anterior (no idéntico esta vez). Artefacto `models/champion/laliga_champion_v1.joblib` regenerado; `src/inference/champion.py` y `app/backend/main.py` sin cambios de código (usan `predict_proba`/`classes_` de forma genérica). Verificado end-to-end con backend+frontend levantados manualmente y predicción real. Suite completa 36/36 en verde.

### [x] T-2.INT Verificar comparabilidad y selección

- Responsable: todo el equipo.
- Dependencias: T-2.1 a T-2.6.
- Acción: verificar versiones de datos, features, splits, métricas, gap, artefactos y uso único del test.
- Criterio de aceptación: ninguna diferencia no aprobada invalida la comparación y el Champion tiene acta de selección.
- Evidencia: checklist firmada y tabla de experimentos consolidada.
- Cierre 2026-07-26: `src.evaluation.champion` valida igualdad de hashes, feature generator y manifest antes de seleccionar; registra el uso final único de test.

## Fase 3 — Integración y Nivel Esencial

### [x] T-3.1 Validar pipeline Champion para inferencia

- Responsable: I1.
- Revisores: I2 e I4.
- Dependencias: T-2.INT.
- Acción: comprobar schema, transformaciones y casos límite.
- Criterio de aceptación: entrenamiento e inferencia usan el mismo pipeline.
- Cierre 2026-07-26: `ChampionPredictor` calcula las mismas `MODEL_FEATURES` desde partidos estrictamente anteriores; prueba de integración compara una fila real de validation con su feature de inferencia.

### [x] T-3.2 Integrar Champion en backend

- Responsable: I4.
- Revisores: I1 e I2.
- Dependencias: T-2.INT, T-1.7.
- Acción: cargar el artefacto real y responder según el contrato.
- Criterio de aceptación: predicción reproducible, versionada y con errores controlados.
- Cierre 2026-07-26: API FastAPI carga el artefacto D y metadata, devuelve contrato v1 y maneja equipos desconocidos, historial insuficiente y modelo no disponible.

### [x] T-3.3 Integrar frontend con predicción real

- Responsable: I3.
- Revisores: I1 e I4.
- Dependencias: T-3.2, T-1.6.
- Acción: sustituir mocks y completar el flujo de usuario.
- Criterio de aceptación: una persona puede introducir datos y comprender el resultado.
- Cierre 2026-07-26: frontend usa `POST /api/v1/predictions`, muestra probabilidades y errores controlados.

### [x] T-3.4 Completar tests esenciales distribuidos

- Responsable: todos.
- Dependencias: T-3.1 a T-3.3.
- Acción: probar datos, métricas, interfaz, backend e integración.
- Criterio de aceptación: suite relevante aprobada y fallos críticos resueltos.
- Evidencia: comandos y resultados.
- Cierre 2026-07-26: `pytest -q -p no:cacheprovider --basetemp=<temporal aislado>` pasa 28 tests; cubre datos, features, candidatos, Champion y API.

### [x] T-3.5 Redactar informe técnico inicial

- Responsable: todos; coordina I2.
- Dependencias: T-2.INT.
- Acción: documentar EDA, candidatos, Champion, métricas, overfitting, errores y limitaciones.
- Criterio de aceptación: cifras coherentes con artefactos y pruebas.
- Cierre 2026-07-26: informe `reports/technical_report.md` enlaza EDA, candidatos, Champion, métricas, errores y limitaciones.

### [x] T-3.6 Ejecutar smoke test esencial

- Responsable: I3 e I4.
- Revisores: I1 e I2.
- Dependencias: T-3.3, T-3.4.
- Acción: ejecutar flujo completo con casos válidos e inválidos.
- Criterio de aceptación: aplicación funcional y evidencia registrada.
- Cierre 2026-07-26: prueba de API válida e inválida incluida en `test_prediction_api_returns_the_versioned_contract_and_controlled_errors`.

### [x] T-3.7 / T-3.INT Verificar cierre del Nivel Esencial

- Responsable: todo el equipo.
- Dependencias: T-3.1 a T-3.6.
- Acción: completar el gate de `3_plan.md`.
- Criterio de aceptación: ningún requisito esencial carece de evidencia.
- Cierre 2026-07-26: gate de `3_plan.md` satisfecho por EDA, Champion reproducible e integrado, métricas/overfitting documentados, aplicación, informe y 28 tests aprobados.

## Fase 4 — Nivel Medio

### [x] T-4.1 Entrenar y comparar ensemble

- Responsable: I1 e I2.
- Revisores: I3 e I4.
- Dependencias: T-3.7.
- Criterio de aceptación: ensemble comparable y documentado.
- Avance I4 2026-07-27: implementado un componente SVC con kernel RBF y calibración explícita de probabilidades mediante `CalibratedClassifierCV(method="temperature")`. El estimador base se ajusta sin probabilidades internas, utiliza `C=0.5`, `gamma="scale"` y balanceo de clases; el calibrador usa cinco folds estratificados dentro de train y `ensemble=False`.
- Protección de datos: entrenamiento con 9.607 partidos, evaluación con 1.197 partidos de validación y 0 filas del test protegido. Se mantienen las features históricas comunes y los splits congelados.
- Resultado de validación: macro-F1 0,484859, accuracy 0,497076, balanced accuracy 0,490231, log loss 1,051532, Brier multiclase 0,634072, ECE 0,070104 y gap train-validación 0,007564.
- Evidencia: `src/ensemble/svc_calibrated.py`, `scripts/run_ensemble_svc_calibrated.py`, `tests/unit/test_calibrated_svc.py` y `reports/experiments/ensemble_svc_calibrated_*`. La comparación documenta también las variantes sigmoid temporal y sigmoid estratificada descartadas.
- Estado: el componente queda listo para revisión e integración, pero T-4.1 sigue abierta hasta combinar los estimadores, comparar el ensemble completo y recibir la revisión de I1–I3.
- Avance 2026-07-27 (I2), primera iteración: implementado `src/candidates/ensemble.py`, votación suave entre A y D sin reajustar hiperparámetros. Resultado: validation macro-F1 0,431291 (por debajo de A y D), gap 0,016469. No desplaza al Champion D. Detalle en `reports/experiments/ensemble_review.md`. Este PR se cerró sin fusionar (decisión del equipo) para retomarlo con el B retunado y los 4 candidatos.
- Avance 2026-07-27 (I2), segunda iteración — ensemble completo A+B+C+D: antes de ensamblar, se corrigieron los dos candidatos descalificados. B (I2) retunado (adelanto de T-4.2 sobre el propio candidato): `HistGradientBoostingClassifier` con `early_stopping=True`, `max_leaf_nodes=19`, `min_samples_leaf=20`, `l2_regularization=0.5`, `class_weight=balanced`, elegido por grid search en validation; gap 0,376 -> 0,042, validation macro-F1 0,479108. C (I3) incorporado por cherry-pick del commit `ffea77e` (rama `feature/t-2.3-modelo-c-actualizado`, aún sin PR): gap 0,256 -> 0,000, validation macro-F1 0,474194. Con los cuatro ya sanos, `src/candidates/ensemble.py` (`build_ensemble_pipeline_abcd`) combina los cuatro pipelines completos por votación suave. Resultado inicial (con D sin calibrar): validation macro-F1 0,454825, gap 0,027714 — por debajo de los cuatro individuales salvo A. No desplazaba al Champion. Detalle completo en `reports/experiments/ensemble_abcd_review.md`. Suite completa en verde.
- Avance 2026-07-27 (I2), tercera iteración — tras integrar la calibración de D (ver nota de T-4.2 más abajo), se regeneró el ensemble de 4 con el D calibrado. **Resultado nuevo: validation macro-F1 0,488281, gap 0,003112 — supera a los cuatro individuales, incluido el Champion (0,484859).** Detalle en la sección "Actualización" de `reports/experiments/ensemble_abcd_review.md`.
- Cierre 2026-07-28: a petición explícita del equipo, el ensemble se promovió formalmente a Champion (ver enmienda en `docs/decisions/0003-four-candidate-models.md` y actualización de T-2.6). T-4.1 queda cerrada: el ensemble es comparable, documentado y ahora también seleccionado.

### [x] T-4.2 Aplicar validación cruzada y tuning

- Responsable: I2 con colaboración de los propietarios de candidatos.
- Dependencias: T-4.1.
- Criterio de aceptación: búsqueda reproducible sin usar test final.
- Avance 2026-07-27 (I2) — retune de B: ver nota en T-4.1 (grid search de 256 combinaciones sobre `validation`, gap 0,376 -> 0,042). Reproducible: `./.venv/Scripts/python.exe scripts/run_candidate_b.py`.
- Avance 2026-07-27 (I2) — integración de la calibración de D en el Champion: `src/candidates/model_d/pipeline.py` deja de usar `probability=True` (deprecado desde sklearn 1.9) y reutiliza `build_calibrated_svc` de I4 (`src/ensemble/svc_calibrated.py`, construido en T-4.1): `CalibratedClassifierCV(method="temperature", cv=StratifiedKFold(5), ensemble=False)`. Validation macro-F1 0,483744 -> 0,484859; gap 0,009166 -> 0,007564. `scripts/select_champion.py` re-ejecutado: D calibrado sigue siendo Champion (decisión tomada solo con `validation`, sin usar test). **Nota de gobernanza:** esto implicó una segunda evaluación del test protegido para D (la primera fue el 26/07 con el D original); el resultado en test fue prácticamente idéntico (macro-F1 0,470529, igual hasta el 6º decimal — mismas predicciones, solo cambian las probabilidades reportadas). `0_constitution.md` establece una única evaluación de test; este caso (actualizar la implementación interna de un Champion ya seleccionado, sin tocar la decisión de cuál candidato gana) no estaba contemplado explícitamente. Queda documentado en `reports/experiments/champion_d_calibration_review.md` para que el equipo decida si amerita una regla nueva en `2_spec.md`. Integración verificada end-to-end: backend + frontend levantados manualmente, predicción real solicitada y validada; suite completa 36/36 en verde.
- Cierre 2026-07-28 (I2) — validación cruzada formal: `src/evaluation/cross_validation.py` aplica `TimeSeriesSplit(n_splits=4)` **exclusivamente sobre `split == "train"`**; `validation` y `test` nunca se leen. Ejecutada para los cuatro candidatos (`scripts/run_cross_validation.py`); resultado: los cuatro mejoran de forma monótona con más historial (macro-F1 ~0,37-0,40 con poco historial hasta ~0,43-0,46 con la ventana completa de train), sin señales de inestabilidad temporal ni degradación. C es el más estable (std 0,024); D el más sensible a la cantidad de datos (std 0,038). No se encontró motivo para cambiar ningún hiperparámetro ya elegido. `experiments_table.csv` actualizada: `cv_summary_reference` ahora apunta a `reports/experiments/candidate_{a,b,c,d}_cv_summary.json` en vez de `not_applied_temporal_holdout_only`. Detalle completo en `reports/experiments/cross_validation_review.md`. 6 tests nuevos (`tests/unit/test_cross_validation.py`); suite completa 56/56 en verde.

### [x] T-4.3 Implementar feedback

- Responsable: I3 e I4.
- Revisores: I1 e I2.
- Dependencias: T-3.7.
- Criterio de aceptación: feedback validado y recuperable.
- Cierre 2026-07-28 (I2, con autorización explícita del equipo para avanzar tareas fuera de su responsabilidad directa, incluida esta): `src/feedback/store.py` implementa un almacén append-only y validado (equipos distintos, `actual_result`/`predicted_result` en {H,D,A}, comentario ≤500 caracteres) sobre `data/feedback/predictions_feedback.csv`; el feedback inválido nunca llega a escribirse. `POST /api/v1/feedback` (`app/backend/main.py`, esquemas en `app/backend/schemas.py`) expone el contrato validado, siguiendo el mismo patrón de error uniforme que `/api/v1/predictions`. No depende de una base de datos (esa es T-5.3); es un CSV recuperable fila a fila vía `load_feedback`. Verificado end-to-end con el backend real: caso válido guardado y recuperado, caso inválido (mismo equipo local/visitante) rechazado con 422. 11 tests nuevos (8 unitarios de `store.py`, 3 de integración del endpoint); suite completa 56/56 en verde.

### [x] T-4.4 Preparar ingestión de datos nuevos

- Responsable: I1 e I4.
- Revisor: I2.
- Dependencias: T-4.3.
- Criterio de aceptación: datos nuevos pueden validarse y reutilizarse sin mezclarse automáticamente con entrenamiento.
- Cierre 2026-07-28 (I2, con autorización explícita del equipo para avanzar tareas fuera de su responsabilidad directa, incluida esta): `src/data/ingestion.py` reutiliza la limpieza ya aprobada de `src/data/laliga_loader.py` (T-1.1/T-1.4) para partidos nuevos en el mismo esquema raw (`Date`, `HomeTeam`, `AwayTeam`, `FTHG`, `FTAG`, `FTR`, ...) sin modificar ese módulo. Valida columnas mínimas, limpieza (misma lógica que las fuentes originales), rechaza duplicados contra `match_id` del histórico y filas no posteriores a la fecha máxima conocida, y escribe los partidos aceptados en `data/processed/staging/pending_matches.csv` — **nunca** en `data/processed/laliga_matches_clean.csv`. Incorporar lo aceptado al entrenamiento requeriría un paso manual y explícito aparte, no implementado aquí a propósito (sería mezcla automática, justo lo que el criterio de aceptación prohíbe). Verificado end-to-end con `scripts/ingest_new_matches.py`: SHA-256 del dataset canónico confirmado idéntico antes y después de la ingesta. 6 tests nuevos (`tests/unit/test_ingestion.py`); suite completa 56/56 en verde.

## Fase 5 — Nivel Avanzado

### [x] T-5.1 Completar tests unitarios y de integración

- Responsable: todos según `2_spec.md`.
- Dependencias: T-3.7.
- Criterio de aceptación: contratos críticos cubiertos y suite aprobada.
- Cierre 2026-07-28 (I2, con autorización explícita del equipo): auditoría de cobertura identificó contratos críticos sin test dedicado: selección de Champion (`src/evaluation/champion.py`), rutas de error de inferencia (`TEAM_NOT_FOUND`, `INSUFFICIENT_HISTORY`, `MODEL_UNAVAILABLE`), los mismos códigos a nivel de API (404/409), `/health`, y el contrato de `src/candidates/common.py` (particiones inválidas, esquema de `experiments_table.csv`). Se añaden `tests/unit/test_champion_selection.py`, `tests/unit/test_champion_inference_errors.py`, `tests/integration/test_backend_contract.py` y `tests/unit/test_candidates_common.py`. 16 tests nuevos; suite completa **72/72 en verde**.

### [x] T-5.2 Dockerizar la solución

- Responsable: I4.
- Revisores: I1 e I3.
- Dependencias: T-3.7.
- Criterio de aceptación: contenedor levanta la aplicación y carga el Champion.
- Cierre 2026-07-28 (I2, con autorización explícita del equipo): `docker/backend.Dockerfile` (FastAPI + Champion), `docker/frontend.Dockerfile` (nginx sirviendo `app/frontend/public`) y `docker-compose.yml` (orquesta `postgres` + `backend` + `frontend`, con `depends_on`/`healthcheck` para que el backend espere a Postgres). El build del backend copia los artefactos ya generados por el pipeline (no re-entrena en el build, sería de varios minutos); prerrequisito documentado en `docker/README.md`. Se detectó y corrigió un problema real: `requirements-backend.txt` no declaraba `pandas`/`numpy`/`scikit-learn`/`joblib`, necesarios para cargar el Champion — sin este fix el contenedor no arrancaba. **Verificación real con `docker compose up --build`:** los tres contenedores arrancan, Postgres queda `healthy`, el backend carga el Champion (`ensemble_abcd_soft_voting_v1`) y sirve una predicción real y un feedback real vía HTTP, ambos persistidos y confirmados con una consulta directa a Postgres dentro del contenedor. El frontend (nginx) responde 200 y se probó en navegador de punta a punta (Girona vs Alaves → Victoria visitante 40%). Stack detenido tras la verificación.

### [x] T-5.3 Conectar persistencia

- Responsable: I3 e I4.
- Revisores: I1 e I2.
- Dependencias: T-4.3.
- Criterio de aceptación: datos persisten tras reinicio y schema está documentado.
- Cierre 2026-07-28 (I2, con autorización explícita del equipo): persistencia en **PostgreSQL** vía SQLAlchemy 2.0 + `psycopg` v3 (`src/persistence/`), configurable por `DATABASE_URL`. Tablas `predictions` y `feedback`, esquema documentado en `docs/database_schema.md`. Integrado en `app/backend/main.py` de forma *best-effort*: si la base de datos no está disponible, `/api/v1/predictions` y `/api/v1/feedback` siguen respondiendo con normalidad (el feedback conserva además su ruta CSV de T-4.3 sin cambios). **Verificación real, no simulada:** contenedor `postgres:16` con volumen nombrado, esquema inicializado, predicción y feedback insertados vía el backend real (`DATABASE_URL` apuntando al contenedor), **contenedor reiniciado (`docker restart`)** y datos confirmados intactos tras el reinicio — la prueba explícita que pide el criterio de aceptación. 4 tests unitarios nuevos (`tests/unit/test_persistence.py`, con SQLite en memoria para no requerir infraestructura en CI; la verificación con Postgres real fue manual y queda documentada). Suite completa 76/76 en verde. Contenedor y volumen de verificación eliminados tras la prueba (no quedan artefactos de infraestructura en el repo).

### [x] T-5.4 Desplegar y verificar

- Responsable: I4 con apoyo de todo el equipo.
- Dependencias: T-5.1 a T-5.3.
- Criterio de aceptación: URL o entorno desplegado funcional, o bloqueo externo claramente documentado.
- Avance I4 2026-07-28: preparada una única imagen Docker desplegable que sirve FastAPI y el frontend desde el mismo dominio, respeta el puerto `PORT` de producción y adapta la cadena PostgreSQL de Render al driver `psycopg`.
- Artefacto: Champion `ensemble_abcd_soft_voting_v1` publicado fuera del historial Git en el release `model-ensemble-abcd-soft-voting-v1`; el build verifica SHA-256 `6333eb87342f9997d764ba416b3a7a434ab2d20df801fa210c0b08bbb7a1bd77`.
- Evidencia local: imagen `laliga-predictor:t54` construida desde cero; smoke test HTTP con raíz 200, `/health` en estado `ok`, `model_loaded=true` y predicción real `Real Madrid`–`Barcelona`.
- Infraestructura: `render.yaml` define servicio web Docker y PostgreSQL gratuitos en Frankfurt.
- Cierre I4 2026-07-28: Blueprint activado desde `develop` y despliegue público operativo en `https://laliga-predictor-grupo4.onrender.com/`. Verificación externa: raíz HTTP 200; `/health` con `status=ok`, `model_loaded=true` y Champion `ensemble_abcd_soft_voting_v1`; predicción Real Madrid–Barcelona `H`, probabilidades sumando 1 y latencia final de 241 ms observados / 50,49 ms internos. La optimización de PR #71 evita regenerar los 11.944 partidos en cada consulta. Suite completa: 80 tests aprobados. Evidencia detallada en `reports/experiments/deployment_verification.md`. T-5.4 y el Nivel Avanzado quedan cerrados.
- Revalidación I4 2026-07-30: tras fusionar PR #78, `develop` (`fb3d021`) se desplegó manualmente porque `autoDeployTrigger: off`. Render quedó `Live` con el Champion `ensemble_abcd_soft_voting_v1`, artefacto SHA-256 `f9c0e93317924613e9dc8fb57125ecd5b227fdb0afa6fc7ec1f6e963407d5696` y dataset SHA-256 `56e59efa9200042f76638beafd47feaf67a41a28c00c02aa521192739a607104`, iguales a los registrados en el repositorio. `/health` respondió `ok`; una predicción Real Madrid–Barcelona devolvió `A`, probabilidades sumando `1` y 340,51 ms internos. Se verificaron además `400 MALFORMED_JSON` y `413 PAYLOAD_TOO_LARGE` en producción. La evidencia vigente queda en `reports/experiments/deployment_verification.md`.

## Fase 6 — Nivel Experto opcional

### [ ] T-6.1 Entrenar red neuronal comparable

- Responsable: por asignar según carga disponible.
- Dependencias: Nivel Avanzado cerrado.
- Criterio de aceptación: mismas particiones, métricas y regla de overfitting.

### [ ] T-6.2 Implementar o simular A/B testing

- Responsable: I2 e I4.
- Dependencias: T-6.1.
- Criterio de aceptación: comparación reproducible con versión de modelo.

### [ ] T-6.3 Medir data drift

- Responsable: I1 e I4.
- Dependencias: datos operativos suficientes.
- Criterio de aceptación: referencia, método, umbrales y limitaciones documentados.

### [ ] T-6.4 Implementar promoción condicionada

- Responsable: I2 e I4.
- Revisores: I1 e I3.
- Dependencias: T-6.2, T-6.3.
- Criterio de aceptación: un modelo inferior no puede reemplazar al Champion.

## Fase 7 — Cierre

### [ ] T-7.1 Revisar métricas y overfitting finales

- Responsable: I2.
- Revisores: I1, I3 e I4.
- Dependencias: último nivel comprometido cerrado.

### [ ] T-7.2 Preparar presentación de negocio

- Responsable: todos; coordina I3.
- Dependencias: T-3.7.
- Criterio de aceptación: problema, solución, impacto, demo y limitaciones comprensibles.

### [ ] T-7.3 Preparar presentación técnica

- Responsable: todos; coordina I4.
- Dependencias: último nivel comprometido cerrado.
- Criterio de aceptación: cada decisión técnica importante tiene evidencia.

### [ ] T-7.4 Completar README y checklist de entrega

- Responsable: todos.
- Dependencias: T-7.1 a T-7.3.
- Criterio de aceptación: app, GitHub, informe, presentaciones, herramienta organizativa y niveles alcanzados están verificados.

## Estado del documento

| Campo | Valor |
|---|---|
| Estado | v1.2 — Nivel Avanzado cerrado con despliegue público verificado |
| Fecha | 28/07/2026 |
| Siguiente trabajo | Decidir si se ejecuta el Nivel Experto opcional o avanzar al cierre T-7.1–T-7.4 |
| Regla | Marcar `[x]` solo con verificación, evidencia y revisión cruzada |
