# Registro de dailys

## Información

- Proyecto: Proyecto 6 — Grupo 4.
- Fecha de entrega: 30/07/2026.
- Scrum Master: Arnaldo.
- Equipo: Arnaldo, Johans, César y Fernanda.

Este documento se actualizará al finalizar cada daily. Solo contendrá información comunicada por el equipo: trabajo realizado, trabajo siguiente, bloqueos, decisiones y evidencias.

## Daily 22/07/2026

### Arnaldo

- Realizado: amplió la especificación del ciclo de vida del dato; desarrolló y documentó el EDA de LaLiga con loader, auditoría, diccionario, visualizaciones y pruebas; configuró GitHub Project con 33 actividades asignadas; revisó y aprobó con el equipo el dataset de LaLiga como dataset canónico.
- Siguiente: cerrar `T-0.2` y `T-0.3` con la decisión de LaLiga e iniciar `T-1.1`: consolidar el mecanismo reproducible de carga, verificar las fuentes y auditar la estructura, las clases y los riesgos de leakage.
- Bloqueos: ninguno.

### Johans

- Realizado: revisó, aprobó y fusionó el PR #2 del EDA de LaLiga; revisó y aprobó con el equipo la selección del dataset de LaLiga.
- Siguiente: completar `T-0.4`, definiendo métrica principal y secundarias, estrategia de partición, semilla y fórmula operativa del gap de overfitting para clasificación multiclase.
- Bloqueos: ninguno.

### César

- Realizado: revisó y aprobó con el equipo la selección del dataset de LaLiga y su enfoque de clasificación multiclase del resultado de los partidos.
- Siguiente: avanzar `T-0.6` con Fer: concretar el contrato de entrada y salida para la predicción de partidos y preparar el diseño del frontend simulado de `T-1.6`.
- Bloqueos: ninguno.

### Fer

- Realizado: revisó con el equipo las fuentes, la viabilidad técnica y los riesgos del dataset de LaLiga, y aprobó su selección como dataset canónico.
- Siguiente: avanzar `T-0.6` con César: definir arquitectura y contrato técnico de inferencia; después preparar el backend simulado de `T-1.7`.
- Bloqueos: ninguno.

### Decisiones y evidencias

- Decisiones: el equipo aprueba el dataset de partidos de LaLiga como dataset canónico. La unidad de análisis será un partido y el objetivo será una clasificación multiclase del resultado: victoria local (`H`), empate (`D`) o victoria visitante (`A`). Se mantendrá una partición temporal para evitar leakage y no se iniciará el entrenamiento hasta cerrar `Data Ready`.
- Issues o PR relacionados: propuesta de dataset y target en `docs/decisions/0001-laliga-dataset-target-proposal.md`; EDA de LaLiga en el PR #2; GitHub Project `Proyecto6-Grupo4`, issues #3–#35.

## Daily 23/07/2026

### Arnaldo

- Realizado: consolidó la selección técnica ya aprobada de LaLiga, la predicción prepartido y el target multiclase `result_ft`; dejó evidencia provisional de `T-1.1`, `T-1.2` y `T-1.3` mediante el loader común, la auditoría, el diccionario de datos, el notebook, el informe del EDA y sus pruebas. Revisó y aprobó técnicamente como I1 las particiones de T-1.5: SHA-256 del dataset, 11.944 índices reproducibles sin duplicados o ausentes, conteos 9.607/1.197/1.140, test protegido y suite 14/14. Ejecutó la revisión I1 de T-0.2b: confirmó la finalidad de predicción, pero no encontró una licencia abierta ni permiso explícito de redistribución para los CSV.
- Siguiente: mantener actualizada la trazabilidad de T-0.2b; solicitar la revisión cruzada de I3/I4 para T-1.5; consolidar en `T-1.1` una carga reproducible con schema, dimensiones y huellas verificadas; completar la auditoría y el contrato de datos de `T-1.2`; y coordinar la revisión cruzada del EDA compartido de `T-1.3`.
- Bloqueos: T-0.2b se cierra el 24/07/2026 con la política documentada de procedencia y redistribución. Siguen pendientes las revisiones cruzadas. La ausencia de César retrasa su revisión como I3 del diccionario y contrato de datos de `T-1.2`.

### Johans

- Realizado: revisó y aprobó con el equipo la selección del dataset de LaLiga; revisó, aprobó y fusionó el PR #2 del EDA de LaLiga.
- Siguiente: completar `T-0.4`, definiendo la métrica principal y las secundarias, la estrategia de partición, la semilla y la fórmula operativa del gap de overfitting para la clasificación multiclase.
- Bloqueos: ninguno.

### César

- Realizado: no informado; ausente por motivos personales.
- Siguiente: retomar, cuando se reincorpore, `T-0.6` con Fernanda y `T-1.6`, además de las revisiones de I3 que tiene asignadas.
- Bloqueos: ausencia por motivos personales.

### Fernanda

- Realizado: confirmó sus responsabilidades iniciales y está trabajando en la rama `feature/i4-backend-mock`, destinada al backend simulado.
- Siguiente: revisar y aprobar la especificación con el equipo (`T-0.1`); analizar la viabilidad de productivización —inferencia, latencia, versionado de datos y modelos, y despliegue—; avanzar el contrato entre frontend y backend con César (`T-0.6`); y crear el backend simulado con validación de entradas y predicciones mock (`T-1.7`). Tras cerrar `Data Ready`, desarrollará su Pipeline D + Modelo D (`T-2.4`) y posteriormente participará en la integración del Champion, las pruebas de backend, Docker y despliegue.
- Bloqueos: la ausencia de César impide cerrar conjuntamente `T-0.6` y limita la revisión cruzada de `T-1.7`; Fernanda puede avanzar un borrador del contrato y el backend mock mientras César se reincorpora.

### Decisiones y evidencias

- Decisiones: se confirma la aprobación técnica de LaLiga como dataset canónico, la unidad partido, el enfoque prepartido y `result_ft` H/D/A. I1 aprueba técnicamente la implementación de particiones de T-1.5. En T-0.2b, I1 decide aplicar una política conservadora: uso local para predicción y no redistribución pública de raw o derivados fila a fila sin permiso escrito. En daily 2026-07-24 el equipo ratificó T-0.2b (uso local, incluida la permanencia de los CSV ya trackeados en Git, sin remediación pendiente), T-1.5 (revisión cruzada de I3/I4) y T-0.5 (cuatro modelos candidatos: regresión logística, gradient boosting, random forest y SVM). `Data Ready` continúa bloqueado por el resto de tareas de Fase 0/1, no por la licencia ni por las particiones. César consta como ausente por motivos personales y sus dependencias inmediatas deberán replanificarse.
- Issues o PR relacionados: PR #2 del EDA de LaLiga; PR #40 de protocolo y particiones; PR #42/#43 de T-0.2b; GitHub issue #41 para T-0.2b, asignado a Arnaldo, ratificado y listo para cerrarse tras la daily 2026-07-24; rama `feature/i4-backend-mock`; evidencias provisionales de `T-1.1`, `T-1.2`, `T-1.3` registradas en `.specify/4_tasks.md`; T-1.5 y T-0.5 cerrados (`docs/decisions/0003-four-candidate-models.md`); GitHub Project `Proyecto6-Grupo4`.

## Daily 24/07/2026

### Arnaldo

- Realizado: cerró `T-0.2b`, completando la revisión de las condiciones de uso y redistribución del dataset de LaLiga y documentando la política de conservación local de los CSV ya incorporados al repositorio, sin remediación pendiente. Actualizó la procedencia y trazabilidad del dataset, reconcilió `.specify/` con las decisiones ratificadas y verificó que `T-0.4`, `T-0.5` y `T-1.5` quedaran reflejadas de forma coherente en el SDD y el backlog.
- Siguiente: cerrar como I1 `T-1.1`, `T-1.2`, `T-1.3` y `T-1.4`: consolidar la conexión reproducible y sus huellas, completar el diccionario y contrato de datos, coordinar la revisión cruzada del EDA e implementar la limpieza común con pruebas. Revisar con Johans la coherencia entre los splits congelados y el preprocesamiento antes de solicitar el gate `Data Ready`.
- Bloqueos: la ausencia de César retrasa su revisión como I3 de `T-1.2` y su participación en el EDA compartido de `T-1.3`. La licencia y las particiones ya no bloquean `Data Ready`.

### Johans

- Realizado: cerró `T-0.4`, definiendo `macro-F1` como métrica principal, las métricas secundarias y la fórmula de overfitting. Cerró `T-1.5` con particiones cronológicas congeladas por temporada, implementadas en `src/evaluation/splits.py` y con el test final protegido. Propuso y registró mediante ADR la asignación de los cuatro modelos candidatos de `T-0.5`: regresión logística, gradient boosting, random forest y SVM. Revisó y ratificó `T-0.2b`, alineando `.specify/`, ADR-0001 y el registro de dailys con la decisión de aceptar los CSV ya trackeados en Git sin remediación pendiente.
- Siguiente: seguir la trazabilidad de `T-0.1` y el avance de `T-0.6`; quedar disponible para revisar `T-1.1`, `T-1.2` y `T-1.4` cuando I1 los cierre; y no comenzar Pipeline B + Modelo B (`T-2.2`) hasta que se cierre `Data Ready`.
- Bloqueos: ninguno de su parte. `Data Ready` (`T-1.8`) continúa abierto por `T-0.6`, `T-1.1`–`T-1.4` y `T-1.6`–`T-1.7`; `T-0.1` ya consta cerrado en `.specify/4_tasks.md`.

### César

- Realizado: ausente.
- Siguiente: retomar, cuando se reincorpore, el contrato frontend/backend de `T-0.6`, el frontend simulado de `T-1.6` y las revisiones cruzadas asignadas a I3.
- Bloqueos: ausencia por motivos personales.

### Fernanda

- Realizado: actualizó `develop`, creó la rama `feature/t-0.6-backend-contract` y revisó la especificación. Comenzó a definir la entrada del backend con `home_team`, `away_team` y `match_date`, y a estudiar una posible estimación de goles mediante Poisson considerando ataque, defensa y localía.
- Siguiente: acordar la arquitectura, las tecnologías, el endpoint, las validaciones, los errores y la respuesta del servicio. Decidir con el equipo si se incluirán probabilidades de goles. Después, implementar el backend mock de `T-1.7`.
- Bloqueos: la ausencia de I3 impide validar el contrato con el frontend, cerrar `T-0.6` y obtener la revisión cruzada de `T-1.7`. Mientras tanto, puede avanzar el borrador del contrato y las reglas de validación.

### Decisiones y evidencias

- Decisiones: se ratifican `T-0.2b`, `T-0.4`, `T-0.5` y `T-1.5`. El protocolo usa `macro-F1` como métrica principal, `gap < 0.05`, semilla `42` y particiones cronológicas: train 1995-96–2019-20, validación 2020-21–2022-23 y test protegido 2023-24–2025-26. Los modelos asignados son regresión logística multinomial para I1, gradient boosting para I2, random forest para I3 y SVM con kernel RBF para I4. `T-0.6` permanece abierto y la posible inclusión de probabilidades de goles deberá aprobarse antes de incorporarse al contrato.
- Issues o PR relacionados: PR #40 de protocolo y particiones; PR #42 y PR #43 de `T-0.2b`; `docs/decisions/0001-laliga-dataset-target-proposal.md`, `docs/decisions/0002-evaluation-protocol-proposal.md` y `docs/decisions/0003-four-candidate-models.md`; `src/evaluation/splits.py`; rama `feature/t-0.6-backend-contract`; backlog actualizado en `.specify/4_tasks.md`.

## Daily 27/07/2026

### Arnaldo

- Realizado: cerró como I1 `T-1.1` a `T-1.4` y el generador común de features históricas `T-1.4a`, con carga reproducible, auditoría de 54 columnas, EDA sin uso del test, limpieza determinista y pruebas de no leakage. Completó Pipeline A + Modelo A (`T-2.1`) y validó la compatibilidad del Champion para inferencia (`T-3.1`).
- Siguiente: verificar reproducibilidad de datos, features y Champion; revisar la coherencia entrenamiento–inferencia y aportar EDA, limitaciones y análisis de errores a la documentación final.
- Bloqueos: ninguno registrado.

### Johans

- Realizado: coordinó el cierre de `Data Ready` (`T-1.8`), entrenó el candidato B (`T-2.2`), consolidó la comparativa A–D (`T-2.5`) y coordinó la selección del Champion (`T-2.6`). El candidato D fue seleccionado por `macro-F1` de validación 0,483744 y gap 0,009166; tras reentrenar con train+validación obtuvo `macro-F1` 0,470529 en el test protegido, utilizado una sola vez.
- Siguiente: revisar las métricas, el gap de overfitting, los errores y la coherencia del informe técnico final.
- Bloqueos: ninguno registrado.

### César

- Realizado: completó el frontend simulado (`T-1.6`), el candidato C (`T-2.3`) y la integración del frontend con la predicción real (`T-3.3`). La interfaz consume `POST /api/v1/predictions`, muestra probabilidades y trata errores controlados.
- Siguiente: revisar el flujo de demo de usuario y contribuir a la presentación de negocio.
- Bloqueos: ninguno registrado.

### Fernanda

- Realizado: cerró el contrato de aplicación (`T-0.6`), implementó el backend mock y posteriormente integró el Champion real (`T-1.7`, `T-3.2`). Completó el candidato D (`T-2.4`), seleccionado como Champion, y participó en el smoke test esencial (`T-3.6`). La API FastAPI devuelve el contrato versionado y controla equipos desconocidos, historial insuficiente y modelo no disponible.
- Siguiente: comprobar la ejecución extremo a extremo, preparar instrucciones técnicas y dejar Docker/despliegue como mejora posterior al Nivel Esencial.
- Bloqueos: ninguno registrado.

### Decisiones y evidencias

- Decisiones: `Data Ready` quedó cerrado el 26/07/2026; los cuatro candidatos se evaluaron con el mismo dataset, splits y features históricas sin leakage. B y C quedaron descartados por sobreajuste. Se seleccionó el candidato D, SVC con kernel RBF, como Champion. El Nivel Esencial (`T-3.7`) se considera cerrado con aplicación integrada, informe técnico y evidencia de pruebas.
- Evidencias: `reports/metrics/data_ready_gate.md`; `reports/experiments/experiments_table.csv`; `reports/experiments/champion_metadata.json`; `reports/experiments/champion_test_metrics.json`; `reports/technical_report.md`; `models/champion/laliga_champion_v1.joblib`; y `pytest -q -p no:cacheprovider --basetemp=<temporal aislado>` con **28 tests aprobados**.

## Daily 28/07/2026

### Arnaldo

- Realizado: integró en `develop` el frontend de `T-1.6` mediante la PR #54 y mantuvo la trazabilidad de los cambios que amplían el producto después del cierre del Nivel Esencial.
- Siguiente: revisar la reproducibilidad de los datos, el preprocesamiento y las features históricas tras los avances de Nivel Medio y Avanzado; confirmar que los artefactos del Champion y la inferencia conservan el contrato de datos.
- Bloqueos: ninguno registrado.

### Johans

- Realizado: completó `T-4.1`–`T-4.4` y `T-5.1`–`T-5.3`: ensemble y validación cruzada temporal, feedback validado, ingesta de datos nuevos sin mezclar entrenamiento, cobertura ampliada de tests, Docker y persistencia PostgreSQL. También actualizó el README como guía de ejecución del proyecto. El ensemble A+B+C+D fue promovido como Champion y las verificaciones alcanzaron 76 tests aprobados antes de los cambios posteriores de despliegue.
- Siguiente: revisar métricas, overfitting, validación cruzada y la documentación final del Champion para el cierre de `T-7.1` y el informe técnico.
- Bloqueos: ninguno registrado.

### César

- Realizado: actualizó el Modelo C para corregir el gap de overfitting, contribuyó a la integración del frontend y preparó la presentación técnica de LaLiga Predictor (`T-7.3`).
- Siguiente: completar la revisión de la experiencia de demo y preparar, junto al equipo, la presentación orientada a negocio y la checklist de entrega.
- Bloqueos: ninguno registrado.

### Fernanda

- Realizado: desplegó la aplicación en Render con PostgreSQL; verificó frontend, API, Champion y predicciones; optimizó la inferencia de más de 36 s a unos 0,54 s; y dejó la suite completa con 80 tests aprobados. La optimización está publicada en la PR #71.
- Siguiente: fusionar la PR #71, ejecutar el despliegue manual en Render, verificar la latencia y cerrar `T-5.4` en `.specify`.
- Bloqueos: ninguno técnico. Pendiente fusionar y redesplegar la PR #71.

### Decisiones y evidencias

- Decisiones: el Champion pasa a ser el ensemble A+B+C+D tras la comparación documentada; las mejoras de Nivel Medio y Avanzado quedan incorporadas sin alterar el dataset canónico ni los splits protegidos. `T-5.4` continúa en progreso hasta que la optimización de la PR #71 esté fusionada, desplegada y comprobada en Render.
- Evidencias: PR #54, PR #63, PR #66–#70 y PR #71; `render.yaml`; `docker-compose.yml`; `docs/database_schema.md`; `reports/experiments/cross_validation_review.md`; `reports/experiments/champion_metadata.json`; y la suite de 80 tests registrada por Fernanda.

## Daily 29/07/2026

### Arnaldo

- Realizado: mantuvo la integración y trazabilidad en `develop` de los avances de aplicación, datos y Champion, incluidos los cambios que cierran el Nivel Avanzado.
- Siguiente: realizar la comprobación final de reproducibilidad del dataset, preprocesamiento, features históricas y compatibilidad del Champion para la entrega.
- Bloqueos: ninguno registrado.

### Johans

- Realizado: corrigió el mapeo de nombres de equipos entre frontend y el catálogo real del backend (PR #73), evitando errores de predicción por discrepancias de nombres. Mantiene como evidencia los cierres de evaluación, ensemble Champion, validación cruzada, Docker, PostgreSQL y README.
- Siguiente: cerrar `T-7.1` con la revisión final de métricas y overfitting, y verificar la coherencia de las cifras entre artefactos, informe y presentación.
- Bloqueos: ninguno registrado.

### César

- Realizado: base de React para integrar con backend y modificación del frontend.
- Siguiente: publicar versión React.
- Bloqueos: de momento ninguno.

### Fernanda

- Realizado: fusionó la optimización de la PR #71, desplegó la aplicación pública en Render con PostgreSQL y cerró `T-5.4`. La URL `https://laliga-predictor-grupo4.onrender.com/` responde correctamente; `/health` informa Champion cargado y una predicción Real Madrid–Barcelona completó en 241 ms observados y 50,49 ms internos. La suite completa alcanza 80 tests aprobados.
- Siguiente: apoyar las comprobaciones finales de aplicación, despliegue y demo, y aportar las evidencias técnicas a la presentación y checklist de entrega.
- Bloqueos: ninguno técnico.

### Decisiones y evidencias

- Decisiones: `T-5.4` y el Nivel Avanzado quedan cerrados. Se prioriza el cierre de Fase 7 (`T-7.1`–`T-7.4`): revisión final de métricas, presentaciones, README, smoke test y checklist, sin añadir alcance de Nivel Experto.
- Evidencias: PR #71, PR #72 y PR #73; `render.yaml`; `reports/experiments/deployment_verification.md`; `https://laliga-predictor-grupo4.onrender.com/`; y `.specify/4_tasks.md` con el cierre de `T-5.4`.

## Próximas dailys

- 30/07/2026.

## Plantilla de actualización

```md
## Daily DD/MM/2026

### Arnaldo

- Realizado:
- Siguiente:
- Bloqueos:

### Johans

- Realizado:
- Siguiente:
- Bloqueos:

### César

- Realizado:
- Siguiente:
- Bloqueos:

### Fernanda

- Realizado:
- Siguiente:
- Bloqueos:

### Decisiones y evidencias

- Decisiones:
- Issues o PR relacionados:
```
