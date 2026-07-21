# Proyecto grupal de clasificación

Repositorio inicial para construir una solución de machine learning de clasificación con cuatro developers y cuatro modelos candidatos.

## Regla de trabajo

Antes de proponer o modificar código es obligatorio leer completamente:

1. `.specify/1_intent.md`.
2. `.specify/2_spec.md`.
3. `.specify/3_plan.md`.
4. `.specify/4_tasks.md`.

La carpeta `.specify/` es la fuente central de verdad. El dataset, el target, los cuatro algoritmos y las tecnologías concretas de aplicación todavía no están seleccionados.

## Estrategia de datos y modelos

1. Selección y conexión únicas al dataset.
2. EDA y limpieza iniciales compartidos.
3. Particiones comunes y congeladas.
4. Cuatro pipelines específicos.
5. Cuatro modelos candidatos comparables.
6. Selección e integración de un Champion.

## Ramas

- `main`: versión estable.
- `develop`: integración.
- `feature/i1-data-foundation`: frente inicial de datos.
- `feature/i2-evaluation-contract`: frente inicial de evaluación.
- `feature/i3-frontend-mock`: frente inicial de frontend.
- `feature/i4-backend-mock`: frente inicial de backend.

Después de los frentes iniciales, las ramas se crearán por ticket y se integrarán mediante Pull Request hacia `develop`.

## Estructura

- `app/`: frontend y backend.
- `data/`: datos raw, intermedios, procesados y feedback.
- `src/data/`: preparación común de datos.
- `src/candidates/`: pipelines y entrenamiento de candidatos A–D.
- `src/evaluation/`: comparación y métricas comunes.
- `models/`: artefactos candidatos, Champion y monitorización.
- `reports/`: experimentos, métricas y figuras.
- `tests/`: pruebas unitarias, de integración y end-to-end.
- `docs/`: documentación y presentaciones.

Las instrucciones de instalación y ejecución se añadirán cuando el equipo apruebe el stack técnico.
