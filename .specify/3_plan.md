# SPEC 3 — Plan de ejecución

## Naturaleza del plan

Este documento define la secuencia, dependencias, riesgos y calendario. Se interpreta bajo `0_constitution.md`; las decisiones técnicas vigentes están en `2_spec.md` y las tareas ejecutables en `4_tasks.md`.

Restricción temporal: ocho días hábiles.

## Registro de avance provisional — 2026-07-22

Se ejecuta en la rama `feature/t-1.3-laliga-eda` un incremento conjunto de T-1.1, T-1.2 y T-1.3 para evaluar la propuesta LaLiga. El incremento produce loader único, huellas de fuentes, auditoría, contrato provisional, notebook, informe y visualizaciones. No crea splits, no entrena modelos y no habilita fases posteriores. El avance solo podrá marcarse terminado cuando se confirmen las dependencias y revisiones de `4_tasks.md`.

## Registro de ampliación provisional — 2026-07-23

La petición incorpora T-1.4 al incremento: se formalizan procedencia, política columna a columna, limpieza de críticos y duplicados, prioridad de fuente en solapamientos y persistencia del dataset limpio. El EDA se regenera únicamente desde `data/processed/laliga_matches_clean.csv`, con dos notebooks ejecutados, once gráficas persistentes, outliers IQR y matrices de confusión de reglas fijas. Se mantiene el bloqueo de splits, entrenamiento y selección de candidatos.

## Decisiones de ejecución resumidas

| ADR | Decisión | Estado |
|---|---|---|
| ADR-01 | LaLiga prepartido, unidad partido y target `result_ft` H/D/A | Aprobada técnicamente |
| ADR-02 | Separación temporal; prohibido split aleatorio por filas como evaluación principal | Aprobada por I1–I4 el 24/07/2026 |
| ADR-03 | Features históricas comunes, cerradas al pasado y calculadas en backend | Contrato preliminar |
| ADR-04 | `macro-F1` principal y gap absoluto `< 0.05` | Aprobado por I1–I4 el 24/07/2026 |
| ADR-05 | React + TypeScript + Vite separado de FastAPI; contrato v1 con local, visitante y fecha; salida H/D/A + probabilidades | Aprobado por I1–I4 el 24/07/2026 (T-0.6). Revisado 2026-07-29: el frontend separado de FastAPI y el contrato v1 se mantienen; la parte de stack (React/TypeScript/Vite) se implementó como HTML+CSS+JS plano servido como estático, ver `2_spec.md`. |
| ADR-06 | Cuotas no obligatorias en el MVP por cobertura limitada | Aprobada en `2_spec.md` |

Fallbacks:

- Si las condiciones de uso impiden redistribuir una fuente, el equipo documentará un mecanismo legítimo de adquisición o sustituirá la fuente antes de entrenar.
- Si un equipo carece de historial suficiente, el backend devolverá un estado controlado o aplicará una regla común aprobada; cada candidato no podrá resolverlo de forma distinta.
- Si frontend y backend separados ponen en riesgo el Nivel Esencial, se permite una aplicación modular única siempre que conserve contratos, validación y pipeline serializado.

## Regla de prioridad

El trabajo seguirá este orden:

1. Decisiones mínimas.
2. Gate `Data Ready`.
3. Cuatro experimentos comparables.
4. Selección e integración del Champion.
5. Cierre del Nivel Esencial.
6. Nivel Medio.
7. Nivel Avanzado.
8. Nivel Experto, solo si no compromete lo anterior.
9. Cierre y defensa.

## Frentes permanentes

### Frente A — Datos + candidato A

Responsable principal: Integrante 1.

- Dataset, conexión, EDA y limpieza comunes.
- Contrato y validación de datos.
- Pipeline A + Modelo A.
- Coherencia de datos durante integración.

### Frente B — Evaluación + candidato B

Responsable principal: Integrante 2.

- Protocolo de partición y evaluación.
- Pipeline B + Modelo B.
- Tabla de experimentos y selección.
- Validación final y monitorización de rendimiento.

### Frente C — Frontend + candidato C

Responsable principal: Integrante 3.

- Flujo de usuario y frontend simulado.
- Pipeline C + Modelo C.
- Integración visual, feedback y demo.
- Pruebas de interfaz.

### Frente D — Backend + candidato D

Responsable principal: Integrante 4.

- Servicio de inferencia simulado.
- Pipeline D + Modelo D.
- Integración, persistencia, Docker y despliegue.
- Pruebas de backend y sistema.

## Fase 0 — Alineación y decisiones mínimas

### Objetivo

Resolver las decisiones que bloquean el inicio técnico.

### Trabajo paralelo

- Integrante 1: coordinar criterios y revisión de datasets candidatos.
- Integrante 2: proponer protocolo de métricas y overfitting según los candidatos.
- Integrante 3: analizar qué variables de cada dataset serían utilizables por una persona usuaria.
- Integrante 4: concretar arquitectura, contrato de predicción prepartido, validaciones, carga del artefacto, latencia, Docker y despliegue.

### Entregables

- Dataset y target aprobados.
- Problema y usuario definidos.
- Métrica principal propuesta.
- Cuatro modelos candidatos acordados.
- Tecnología de aplicación acordada.
- Estrategia Git aplicada y herramienta organizativa acordada.

### Gate

No se programa una solución dependiente de estas decisiones hasta registrarlas en `2_spec.md`. Los únicos adelantos permitidos son spikes identificados expresamente en `4_tasks.md`, sin splits ni entrenamiento.

## Fase 1 — Dataset común y `Data Ready`

### Objetivo

Crear una base común, reproducible y aprobada para los cuatro experimentos.

### Trabajo paralelo

- Integrante 1: conexión común, auditoría, consolidación del EDA y limpieza.
- Integrante 2: particiones, métricas, fórmula de overfitting y formato de experimentos.
- Integrante 3: mock de frontend y validación de inputs potenciales.
- Integrante 4: stub de backend para `home_team`, `away_team` y `match_date`, validación del payload, respuesta mock versionada y prueba temprana de entorno/Docker.
- Todos: EDA dividido por preguntas y revisión de decisiones de limpieza.

### Entregables

- Dataset accesible sin duplicar mecanismos de carga.
- EDA común.
- Reglas de limpieza reproducibles.
- Contrato de datos.
- Splits congelados.
- Contrato de experimentación.
- Frontend y backend simulados cuando la arquitectura esté aprobada.

### Verificación

Debe completarse toda la checklist `Data Ready` de `2_spec.md`.

### Riesgos

- Las condiciones de uso y redistribución de las fuentes todavía no están aprobadas.
- Las cuotas y estadísticas detalladas solo cubren 380 partidos y no representan el histórico completo.
- Un split aleatorio por filas sobreestimaría la generalización temporal.
- Las features agregadas sin `shift(1)` filtrarían el resultado del partido actual. T-1.4a es la tarea bloqueante que implementa y prueba el generador histórico común antes de `Data Ready`.
- Equipos ascendidos o categorías no vistas pueden romper codificación e inferencia.
- Elegir variables que no existirían durante una predicción real.
- Introducir leakage durante limpieza o partición.
- Permitir que cada candidato utilice datos diferentes.
- Diseñar frontend o backend antes de conocer el contrato de datos.

## Fase 2 — Cuatro pipelines y modelos en paralelo

### Objetivo

Entrenar cuatro candidatos comparables sin duplicar la preparación común.

### Trabajo paralelo

- Integrante 1: Pipeline A + Modelo A.
- Integrante 2: Pipeline B + Modelo B.
- Integrante 3: Pipeline C + Modelo C, manteniendo avance del frontend.
- Integrante 4: Pipeline D + Modelo D, manteniendo avance del backend.

### Entregables por candidato

- Pipeline reproducible.
- Modelo entrenado.
- Parámetros registrados.
- Métricas train/validación.
- Gap de overfitting.
- Matriz de confusión.
- Análisis de errores inicial.
- Artefacto serializable.
- Tests básicos.

### Verificación

- Los cuatro candidatos usan la misma versión de datos y splits.
- Ningún pipeline ha ajustado transformaciones con validación o test.
- Los resultados siguen el mismo formato.

### Riesgos

- Dedicar demasiado tiempo al tuning antes de tener cuatro resultados mínimos.
- Crear pipelines incompatibles con inferencia.
- Que los roles de frontend y backend abandonen sus frentes permanentes durante el entrenamiento.

## Fase 3 — Comparación e integración esencial

### Objetivo

Seleccionar el Champion e integrarlo en un flujo completo de predicción.

### Trabajo paralelo

- Integrante 1: validar pipeline y contrato de datos del candidato seleccionado.
- Integrante 2: consolidar comparación, overfitting y análisis de errores.
- Integrante 3: sustituir mocks por el contrato real y completar el flujo de usuario.
- Integrante 4: cargar el artefacto real y completar el servicio de inferencia.
- Todos: revisión de selección, pruebas e informe.

### Entregables

- Tabla comparativa.
- Decisión Champion documentada.
- Artefacto versionado.
- Flujo frontend-backend o aplicación modular funcional.
- Predicción completa.
- Informe técnico inicial.
- Evidencia de overfitting inferior al 5 %.

### Gate `Nivel Esencial cerrado`

- EDA y visualizaciones completos.
- Champion funcional y reproducible.
- Métricas obligatorias documentadas.
- Overfitting demostrado.
- Aplicación funcional.
- Análisis de errores e interpretación.
- Pruebas esenciales ejecutadas.
- Instrucciones de ejecución disponibles.

## Fase 4 — Nivel Medio

### Objetivo

Mejorar robustez y preparar aprendizaje con datos de uso.

### Trabajo paralelo

- Integrantes 1 y 2: ensemble, validación cruzada, tuning y reevaluación.
- Integrantes 3 y 4: feedback y recogida de datos nuevos.
- Todos: revisión de métricas, persistencia y documentación.

### Gate

- Ensemble comparable.
- Validación cruzada registrada.
- Tuning documentado.
- Feedback persistente.
- Datos nuevos recuperables para futuro reentrenamiento.

## Fase 5 — Nivel Avanzado

### Objetivo

Hacer la solución reproducible, comprobable y desplegable.

### Trabajo paralelo

- Integrante 1: tests de datos y preprocesamiento.
- Integrante 2: tests de métricas y rendimiento.
- Integrante 3: tests de interfaz y flujo; colaboración en persistencia.
- Integrante 4: tests de backend, Docker y despliegue.
- Todos: smoke test, documentación y correcciones.

### Gate

- Tests mínimos aprobados.
- Docker funcional.
- Persistencia conectada.
- Despliegue verificado o bloqueo externo documentado.

## Fase 6 — Nivel Experto opcional

### Objetivo

Añadir experimentación MLOps sin comprometer el sistema estable.

### Trabajo distribuido

- Integrante 1: perfil de referencia y calidad de datos para drift.
- Integrante 2: evaluación de red neuronal, A/B y reglas de promoción.
- Integrante 3: visualización de feedback o monitorización.
- Integrante 4: instrumentación, versionado y ejecución controlada.

### Gate

- Red neuronal comparable.
- A/B testing real o simulado con evidencia.
- Drift medible.
- Promoción segura y condicionada.
- Ninguna automatización reemplaza el Champion sin controles explícitos.

## Fase 7 — Cierre y defensa

### Objetivo

Congelar la entrega y asegurar coherencia entre código, informe y presentaciones.

### Trabajo compartido

- Smoke test completo.
- Revisión final de métricas y overfitting.
- Informe técnico.
- Presentación de negocio.
- Presentación técnica.
- README y enlaces de organización.
- Checklist de consigna.

### Regla de congelación

Después del freeze solo se aceptarán correcciones verificadas que no amplíen el alcance ni pongan en riesgo la demo.

## Planificación de los ocho días

| Día | Fecha | Objetivo de cierre |
|---:|---|---|
| 1 | 21/07 | Bootstrap, ramas, roles y Specify inicial |
| 2 | 22/07 | Selección técnica LaLiga, loader, auditoría y EDA |
| 3 | 23/07 | Preprocesamiento reproducible, reconciliación SDD y procedencia |
| 4 | 24/07 | Licencia, protocolo de evaluación, features, splits, candidatos y contrato de aplicación |
| 5 | 27/07 | `Data Ready` y cuatro candidatos mínimos en paralelo |
| 6 | 28/07 | Comparación, selección del Champion y primera integración |
| 7 | 29/07 | Aplicación esencial, tests, informe y correcciones |
| 8 | 30/07 | Smoke test, freeze, README, presentaciones y defensa |

Reglas del calendario:

- Si `Data Ready` no cierra el 24/07, se replantea alcance o fuente; no se compensa entrenando con decisiones abiertas.
- Los cuatro integrantes permanecen activos y todo frente crítico tiene revisor.
- El primer flujo esencial completo precede cualquier esfuerzo significativo de niveles superiores.
- La tarde del 29/07 y el 30/07 se reservan para integración, correcciones y defensa.

## Estado del documento

| Campo | Valor |
|---|---|
| Estado | v1.0 — plan reconciliado con LaLiga y fecha de entrega |
| Fecha | 23/07/2026 |
| Próximo gate | Cerrar T-1.4a/T-1.6–T-1.7 para verificar `Data Ready` |
