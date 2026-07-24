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
| Licencia | Cerrado | T-0.2b: ratificado por el equipo en daily 2026-07-24; uso local aceptado, incluida la permanencia de los CSV ya trackeados en Git |
| Evaluación | Cerrado | T-0.4/T-1.5: métrica, gap, ventanas temporales y particiones ratificados por el equipo en daily 2026-07-24 |
| Candidatos | Cerrado | T-0.5: cuatro algoritmos asignados, ver `docs/decisions/0003-four-candidate-models.md` |
| Aplicación | En progreso | T-0.6: arquitectura y contrato definitivo |
| `Data Ready` | Abierto | T-1.8 y checklist de `2_spec.md` |
| Nivel Esencial | No iniciado | Requiere `Data Ready` |

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

### [~] T-0.6 Definir aplicación y contratos preliminares

- Responsable: I3 e I4.
- Revisores: I1 e I2.
- Dependencias: T-0.3.
- Requisitos: RF-01–RF-06, RNF-02–RNF-06.
- Acción: aprobar tecnología, separación lógica o física, endpoints, entrada, salida, errores, latencia y versionado.
- Criterio de aceptación: frontend y backend pueden avanzar con mocks compatibles.
- Evidencia actual: contrato JSON preliminar en `2_spec.md`; faltan ruta, códigos HTTP y decisión de arquitectura.

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

### [~] T-1.1 Implementar conexión única al dataset

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

### [~] T-1.2 Crear diccionario y auditoría de datos

- Responsable: I1.
- Revisor: I3.
- Dependencias: T-1.1.
- Requisito: ML-01.
- Acción: documentar columnas, tipos, target, identificadores, disponibilidad y riesgos.
- Criterio de aceptación: todas las variables tienen rol y descripción.
- Evidencia: diccionario de datos revisado.
- Evidencia provisional: `reports/metrics/data_dictionary.csv`, `reports/metrics/missingness.csv` y `reports/metrics/eda_summary.json`. Pendiente revisión de I3.
- Cierre técnico I1 2026-07-24: diccionario regenerado para las 54 columnas, con tipo, rol, disponibilidad, tratamiento de nulos y riesgo de leakage. La evidencia queda lista para revisión de I3.

### [~] T-1.3 Realizar EDA compartido

- Responsable: todos; coordina I1.
- Dependencias: T-1.1, T-1.2.
- Requisitos: ML-01, ML-06.
- Acción: dividir preguntas de análisis entre los cuatro y consolidar un único EDA.
- Criterio de aceptación: nulos, duplicados, distribuciones, target, relaciones, correlaciones y leakage analizados.
- Evidencia: notebook o informe reproducible con interpretaciones.
- Evidencia provisional: `notebooks/01_laliga_eda.ipynb`, `reports/laliga_eda.md` y once figuras persistentes en `reports/figures/`, incluidas outliers y dos matrices de confusión descriptivas. Análisis técnico completo; pendiente revisión cruzada de los cuatro integrantes.
- Cierre técnico I1 2026-07-24: EDA regenerado con 11 figuras, auditoría de nulos/duplicados/target, análisis temporal, outliers, baseline descriptivo y matriz de leakage. El EDA usa exclusivamente train+validación (10.804 filas); el test 2023-24–2025-26 queda excluido. Verificación registrada en `reports/metrics/eda_verification.md`; pendiente revisión cruzada humana.

### [~] T-1.4 Implementar limpieza común

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

### [ ] T-1.6 Crear frontend simulado

- Responsable: I3.
- Revisor: I4.
- Dependencias: T-0.6, T-1.2.
- Requisitos: RF-01, RF-03–RF-06.
- Acción: implementar o diseñar el flujo con respuestas mock según la arquitectura aprobada.
- Criterio de aceptación: formulario, resultado y error pueden demostrarse sin modelo definitivo.
- Evidencia: prueba visual o test de interfaz.

### [ ] T-1.7 Crear backend de inferencia simulado

- Responsable: I4.
- Revisor: I3.
- Dependencias: T-0.6, T-1.2.
- Requisitos: RF-01–RF-06, RNF-02–RNF-06.
- Acción: implementar el contrato mock con `home_team`, `away_team` y `match_date`; devolver `H/D/A`, probabilidades, versiones, latencia y errores uniformes.
- Criterio de aceptación: contrato consumible por frontend.
- Verificación: fixtures válidos e inválidos compartidos con I3.
- Evidencia: prueba de contrato o llamada reproducible, comandos y resultados.

### [ ] T-1.8 / T-1.INT Verificar gate `Data Ready`

- Responsable: todo el equipo; coordina I2.
- Dependencias: T-0.1, T-0.2b, T-0.4, T-0.5 y T-1.1 a T-1.7.
- Acción: completar la checklist de `2_spec.md`.
- Criterio de aceptación: no quedan decisiones de datos, evaluación o candidatos que bloqueen el entrenamiento.
- Evidencia: checklist completada y revisión cruzada.

## Fase 2 — Cuatro candidatos en paralelo

### [ ] T-2.1 Desarrollar Pipeline A + Modelo A

- Responsable: I1.
- Revisor: I2.
- Dependencias: T-1.8.
- Acción: crear, entrenar, evaluar, serializar y documentar el candidato A.
- Criterio de aceptación: cumple el contrato común de experimentación.
- Evidencia: pipeline, artefacto, métricas, tests y registro.

### [ ] T-2.2 Desarrollar Pipeline B + Modelo B

- Responsable: I2.
- Revisor: I3.
- Dependencias: T-1.8.
- Acción: crear, entrenar, evaluar, serializar y documentar el candidato B.
- Criterio de aceptación: cumple el contrato común de experimentación.
- Evidencia: pipeline, artefacto, métricas, tests y registro.

### [ ] T-2.3 Desarrollar Pipeline C + Modelo C

- Responsable: I3.
- Revisor: I4.
- Dependencias: T-1.8.
- Acción: crear, entrenar, evaluar, serializar y documentar el candidato C sin abandonar el frente de frontend.
- Criterio de aceptación: cumple el contrato común de experimentación y el frontend sigue integrable.
- Evidencia: pipeline, artefacto, métricas, tests y registro.

### [ ] T-2.4 Desarrollar Pipeline D + Modelo D

- Responsable: I4.
- Revisor: I1.
- Dependencias: T-1.8.
- Acción: crear, entrenar, evaluar, serializar y documentar el candidato D sin abandonar el frente de backend.
- Criterio de aceptación: cumple el contrato común de experimentación y el backend sigue integrable.
- Evidencia: pipeline, artefacto, métricas, tests y registro.

### [ ] T-2.5 Consolidar tabla de experimentos

- Responsable: I2.
- Revisores: I1, I3 e I4.
- Dependencias: T-2.1 a T-2.4.
- Acción: verificar comparabilidad y registrar resultados de los cuatro candidatos.
- Criterio de aceptación: ninguna comparación usa datos, métricas o reglas diferentes sin explicarlo.
- Evidencia: tabla completa y observaciones de calidad.
- Adelanto 2026-07-24 (spike, no cierra la tarea): plantilla vacía preparada en `reports/experiments/experiments_table.csv` (filas A–D en `status=pending`, sin resultados) y `reports/experiments/README.md` con el significado de cada columna y las reglas heredadas de `2_spec.md`/`0_constitution.md` (no usar el split de test, mismo `data_version_sha256` para los cuatro candidatos, no editar `candidate_id`/`member`/`algorithm` sin actualizar la ADR 0003). Sigue en `[ ]`: no hay resultados porque T-2.1–T-2.4 no han empezado.

### [ ] T-2.6 Seleccionar y versionar Champion

- Responsable: todo el equipo; coordina I2.
- Dependencias: T-2.5.
- Requisitos: ML-03–ML-05.
- Acción: seleccionar con validación, congelar la decisión y solo después evaluar una vez el test final.
- Criterio de aceptación: Champion cumple overfitting, integración y métricas aprobadas.
- Evidencia: decisión, metadata, métricas finales y artefacto completo.

### [ ] T-2.INT Verificar comparabilidad y selección

- Responsable: todo el equipo.
- Dependencias: T-2.1 a T-2.6.
- Acción: verificar versiones de datos, features, splits, métricas, gap, artefactos y uso único del test.
- Criterio de aceptación: ninguna diferencia no aprobada invalida la comparación y el Champion tiene acta de selección.
- Evidencia: checklist firmada y tabla de experimentos consolidada.

## Fase 3 — Integración y Nivel Esencial

### [ ] T-3.1 Validar pipeline Champion para inferencia

- Responsable: I1.
- Revisores: I2 e I4.
- Dependencias: T-2.INT.
- Acción: comprobar schema, transformaciones y casos límite.
- Criterio de aceptación: entrenamiento e inferencia usan el mismo pipeline.

### [ ] T-3.2 Integrar Champion en backend

- Responsable: I4.
- Revisores: I1 e I2.
- Dependencias: T-2.INT, T-1.7.
- Acción: cargar el artefacto real y responder según el contrato.
- Criterio de aceptación: predicción reproducible, versionada y con errores controlados.

### [ ] T-3.3 Integrar frontend con predicción real

- Responsable: I3.
- Revisores: I1 e I4.
- Dependencias: T-3.2, T-1.6.
- Acción: sustituir mocks y completar el flujo de usuario.
- Criterio de aceptación: una persona puede introducir datos y comprender el resultado.

### [ ] T-3.4 Completar tests esenciales distribuidos

- Responsable: todos.
- Dependencias: T-3.1 a T-3.3.
- Acción: probar datos, métricas, interfaz, backend e integración.
- Criterio de aceptación: suite relevante aprobada y fallos críticos resueltos.
- Evidencia: comandos y resultados.

### [ ] T-3.5 Redactar informe técnico inicial

- Responsable: todos; coordina I2.
- Dependencias: T-2.INT.
- Acción: documentar EDA, candidatos, Champion, métricas, overfitting, errores y limitaciones.
- Criterio de aceptación: cifras coherentes con artefactos y pruebas.

### [ ] T-3.6 Ejecutar smoke test esencial

- Responsable: I3 e I4.
- Revisores: I1 e I2.
- Dependencias: T-3.3, T-3.4.
- Acción: ejecutar flujo completo con casos válidos e inválidos.
- Criterio de aceptación: aplicación funcional y evidencia registrada.

### [ ] T-3.7 / T-3.INT Verificar cierre del Nivel Esencial

- Responsable: todo el equipo.
- Dependencias: T-3.1 a T-3.6.
- Acción: completar el gate de `3_plan.md`.
- Criterio de aceptación: ningún requisito esencial carece de evidencia.

## Fase 4 — Nivel Medio

### [ ] T-4.1 Entrenar y comparar ensemble

- Responsable: I1 e I2.
- Revisores: I3 e I4.
- Dependencias: T-3.7.
- Criterio de aceptación: ensemble comparable y documentado.

### [ ] T-4.2 Aplicar validación cruzada y tuning

- Responsable: I2 con colaboración de los propietarios de candidatos.
- Dependencias: T-4.1.
- Criterio de aceptación: búsqueda reproducible sin usar test final.

### [ ] T-4.3 Implementar feedback

- Responsable: I3 e I4.
- Revisores: I1 e I2.
- Dependencias: T-3.7.
- Criterio de aceptación: feedback validado y recuperable.

### [ ] T-4.4 Preparar ingestión de datos nuevos

- Responsable: I1 e I4.
- Revisor: I2.
- Dependencias: T-4.3.
- Criterio de aceptación: datos nuevos pueden validarse y reutilizarse sin mezclarse automáticamente con entrenamiento.

## Fase 5 — Nivel Avanzado

### [ ] T-5.1 Completar tests unitarios y de integración

- Responsable: todos según `2_spec.md`.
- Dependencias: T-3.7.
- Criterio de aceptación: contratos críticos cubiertos y suite aprobada.

### [ ] T-5.2 Dockerizar la solución

- Responsable: I4.
- Revisores: I1 e I3.
- Dependencias: T-3.7.
- Criterio de aceptación: contenedor levanta la aplicación y carga el Champion.

### [ ] T-5.3 Conectar persistencia

- Responsable: I3 e I4.
- Revisores: I1 e I2.
- Dependencias: T-4.3.
- Criterio de aceptación: datos persisten tras reinicio y schema está documentado.

### [ ] T-5.4 Desplegar y verificar

- Responsable: I4 con apoyo de todo el equipo.
- Dependencias: T-5.1 a T-5.3.
- Criterio de aceptación: URL o entorno desplegado funcional, o bloqueo externo claramente documentado.

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
| Estado | v1.0 — T-0.2b, T-0.4, T-0.5 y T-1.5 ratificados en daily 2026-07-24 |
| Fecha | 24/07/2026 |
| Siguiente trabajo bloqueante | T-0.6; T-1.1–T-1.4 y T-1.6–T-1.7 antes de `T-1.8` |
| Regla | Marcar `[x]` solo con verificación, evidencia y revisión cruzada |
