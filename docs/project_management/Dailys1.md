# Registro de dailys

## Información

- Proyecto: Proyecto 6 — Grupo 4.
- Fecha de entrega: 30/07/2026.
- Scrum Master: Arnaldo.
- Equipo: Arnaldo, Johans, César y Fer.

Este documento se actualizará al finalizar cada daily. Solo contendrá información comunicada por el equipo: trabajo realizado, trabajo siguiente, bloqueos, decisiones y evidencias.

## Daily 22/07/2026

### Arnaldo

- Realizado: amplió la especificación del ciclo de vida del dato; desarrolló y documentó el EDA provisional de LaLiga con loader, auditoría, diccionario, visualizaciones y pruebas; configuró GitHub Project con 33 actividades asignadas; revisó y aprobó con el equipo el nuevo dataset canónico de alfabeto dactilológico LSE.
- Siguiente: cerrar `T-0.2` y `T-0.3` con la decisión LSE e iniciar `T-1.1`: validar la descarga recomendada de resolución 192×192, verificar su MD5 y auditar estructura, clases y variantes antes de diseñar el loader común.
- Bloqueos: ninguno.

### Johans

- Realizado: revisó, aprobó y fusionó el PR #2 del EDA provisional de LaLiga; revisó y aprobó con el equipo la selección del dataset LSE.
- Siguiente: completar `T-0.4`, definiendo métrica principal y secundarias, estrategia de partición, semilla y fórmula operativa del gap de overfitting para clasificación multiclase.
- Bloqueos: ninguno.

### César

- Realizado: revisó y aprobó con el equipo la selección del dataset LSE y su enfoque de clasificación de signos estáticos.
- Siguiente: avanzar `T-0.6` con Fer: concretar el contrato de entrada y salida de imágenes y preparar el diseño del frontend simulado de `T-1.6`.
- Bloqueos: ninguno.

### Fer

- Realizado: documentó la fuente Zenodo, licencia, justificación, riesgos, política de adquisición y contrato preliminar del dataset LSE; revisó y aprobó con el equipo su selección como dataset canónico.
- Siguiente: avanzar `T-0.6` con César: definir arquitectura y contrato técnico de inferencia; después preparar el backend simulado de `T-1.7`.
- Bloqueos: ninguno.

### Decisiones y evidencias

- Decisiones: el equipo aprueba el Spanish Sign Language (LSE) Fingerspelling Dataset como dataset canónico. El alcance se limita a clasificar 23 signos estáticos; se evaluará primero la resolución 192×192 y una sola representación canónica. Las variantes de una misma captura permanecerán agrupadas para evitar leakage y no se iniciará entrenamiento hasta cerrar `Data Ready`.
- Issues o PR relacionados: especificación del dataset en `.specify/5_dataset.md` (commit `29c3253`); EDA provisional de LaLiga en PR #2 como evidencia de evaluación de candidato; GitHub Project `Proyecto6-Grupo4`, issues #3–#35.

## Próximas dailys

- 23/07/2026.
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
