# SPEC 3 — Plan de ejecución

## Naturaleza del plan

Este documento define la secuencia y las dependencias del proyecto. El calendario diario definitivo se cerrará cuando se aprueben dataset, arquitectura y modelos candidatos. La estrategia Git y la estructura inicial ya están definidas en `2_spec.md`.

Restricción temporal: ocho días hábiles.

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

- Dataset, conexión, auditoría, EDA y limpieza comunes.
- Diccionario, contrato, validación y ejemplos de datos.
- Capa común de preprocesamiento + Pipeline A + Modelo A.
- Coherencia de datos desde entrenamiento hasta inferencia, feedback y drift.

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
- Integrante 4: analizar viabilidad de productivización, carga y despliegue.

### Entregables

- Dataset y target aprobados.
- Problema y usuario definidos.
- Métrica principal propuesta.
- Cuatro modelos candidatos acordados.
- Tecnología de aplicación acordada.
- Estrategia Git aplicada y herramienta organizativa acordada.

### Gate

No se programa una solución dependiente de estas decisiones hasta registrarlas en `2_spec.md`.

## Fase 1 — Dataset común y `Data Ready`

### Objetivo

Crear una base común, reproducible y aprobada para los cuatro experimentos.

### Trabajo paralelo

- Integrante 1: conexión común, auditoría, consolidación del EDA, diccionario, contrato y capa común de preprocesamiento.
- Integrante 2: particiones, métricas, fórmula de overfitting y formato de experimentos.
- Integrante 3: mock de frontend y validación de inputs potenciales.
- Integrante 4: stub de backend, mecanismo preliminar de carga y prueba temprana de entorno/Docker.
- Todos: EDA dividido por preguntas y revisión de decisiones de limpieza.

### Entregables

- Dataset accesible sin duplicar mecanismos de carga.
- EDA común.
- Reglas de limpieza reproducibles.
- Contrato de datos con rangos, categorías, obligatoriedad y ejemplos válidos e inválidos.
- Capa común de preprocesamiento definida sin ajustar, preparada para ajustarse solo con entrenamiento tras congelar los splits y reutilizarse en inferencia.
- Splits congelados.
- Contrato de experimentación.
- Frontend y backend simulados cuando la arquitectura esté aprobada.

### Verificación

Debe completarse toda la checklist `Data Ready` de `2_spec.md`.

### Riesgos

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

- Integrante 1: validar pipeline y contrato de datos del candidato seleccionado con categorías desconocidas, nulos, límites y entradas incorrectas.
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

- Integrante 1: perfil estadístico de referencia y calidad de datos operativos y de feedback para drift.
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

La asignación diaria definitiva está pendiente. Al aprobarla deberá cumplir:

- Los cuatro integrantes activos desde el primer día.
- Trabajo en paralelo siempre que sea posible.
- `Data Ready` temprano.
- Primera versión esencial completa antes de dedicar esfuerzo significativo a niveles superiores.
- Tiempo reservado para integración, pruebas, correcciones y defensa.
- Ningún frente crítico asignado a una sola persona sin revisión.
