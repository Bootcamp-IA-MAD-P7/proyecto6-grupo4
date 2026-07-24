# Registro de dailys

## Información

- Proyecto: Proyecto 6 — Grupo 4.
- Fecha de entrega: 30/07/2026.
- Scrum Master: Arnaldo.
- Equipo: Arnaldo, Johans, César y Fer.

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
- Siguiente: obtener ratificación I2/I3/I4 de T-0.2b y preparar un PR que retire los datasets fila a fila del repositorio público o documente permiso escrito; solicitar la revisión cruzada de I3/I4 para T-1.5; consolidar en `T-1.1` una carga reproducible con schema, dimensiones y huellas verificadas; completar la auditoría y el contrato de datos de `T-1.2`; y coordinar la revisión cruzada del EDA compartido de `T-1.3`.
- Bloqueos: T-0.2b queda bloqueada porque la redistribución pública no está demostrada; faltan ratificación I2/I3/I4 y retirar o autorizar los CSV ya versionados. También siguen pendientes las revisiones cruzadas. La ausencia de César retrasa su revisión como I3 del diccionario y contrato de datos de `T-1.2`.

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

## Próximas dailys

- 24/07/2026.
- 27/07/2026.
- 28/07/2026.
- 29/07/2026.
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

### Fer

- Realizado:
- Siguiente:
- Bloqueos:

### Decisiones y evidencias

- Decisiones:
- Issues o PR relacionados:
```
