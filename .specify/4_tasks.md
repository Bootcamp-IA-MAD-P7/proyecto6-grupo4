# SPEC 4 — Backlog de tareas

## Protocolo de ejecución

Antes de comenzar una tarea:

1. Leer completamente `.specify/`.
2. Confirmar que las dependencias están satisfechas.
3. Confirmar responsable, revisor y archivos afectados.
4. Usar la estrategia Git aprobada.
5. No ampliar el alcance sin actualizar la tarea.

Antes de marcarla como terminada:

1. Ejecutar la verificación indicada.
2. Registrar la evidencia.
3. Actualizar documentación afectada.
4. Obtener la revisión cruzada.
5. Confirmar que no se rompe el Nivel Esencial.

## Estados

- `[ ]`: pendiente.
- `[~]`: en progreso.
- `[x]`: completada y verificada.
- `[!]`: bloqueada.
- `[-]`: cancelada o no aplica.

## Roles

- I1: Datos y ciclo de vida del dato + Pipeline A + Modelo A.
- I2: Evaluación y ciclo de vida del modelo + Pipeline B + Modelo B.
- I3: Frontend y producto + Pipeline C + Modelo C.
- I4: Backend, integración y despliegue + Pipeline D + Modelo D.

Los nombres de las personas se incorporarán cuando el equipo confirme la asignación.

## Fase 0 — Decisiones bloqueantes

### [ ] T-0.1 Revisar y aprobar `.specify/`

- Responsable: todo el equipo.
- Revisor: todo el equipo.
- Dependencias: ninguna.
- Acción: leer los cinco documentos, registrar dudas y aprobar o corregir el contrato inicial.
- Criterio de aceptación: todos entienden el flujo común de datos y los cuatro pipelines individuales.
- Evidencia: aprobación registrada por el equipo.

### [ ] T-0.2 Evaluar datasets candidatos

- Responsable: I1, con aportes de I2, I3 e I4.
- Dependencias: T-0.1.
- Acción: comparar candidatos por target, tamaño, licencia, leakage, interpretabilidad, balance y viabilidad de aplicación.
- Criterio de aceptación: tabla de candidatos con ventajas, riesgos y recomendación.
- Evidencia: decisión registrada en `2_spec.md` y ficha comparativa en `5_dataset.md`.
- Aporte I4 registrado: viabilidad preliminar de productivización, almacenamiento y despliegue del dataset LSE en `5_dataset.md`.

### [ ] T-0.3 Definir problema, usuarios y target

- Responsable: todo el equipo; coordina I1.
- Dependencias: T-0.2.
- Acción: aprobar problema de negocio, usuario, unidad de predicción, target y clases.
- Criterio de aceptación: el equipo puede explicar qué se predice, para quién y con qué utilidad.
- Evidencia: `1_intent.md` y `2_spec.md` actualizados.

### [ ] T-0.4 Definir protocolo de evaluación

- Responsable: I2.
- Revisor: I1.
- Dependencias: T-0.3.
- Acción: proponer métrica principal, secundarias, splits, semilla y fórmula de overfitting.
- Criterio de aceptación: protocolo aprobado por los cuatro integrantes.
- Evidencia: contrato registrado en `2_spec.md`.

### [ ] T-0.5 Elegir cuatro modelos candidatos

- Responsable: todo el equipo; coordina I2.
- Dependencias: T-0.3, T-0.4.
- Acción: asignar un algoritmo a cada integrante y justificar diversidad y viabilidad.
- Criterio de aceptación: candidatos A, B, C y D registrados sin duplicación injustificada.
- Evidencia: tabla de decisiones de `2_spec.md` actualizada.

### [ ] T-0.6 Definir aplicación y contratos preliminares

- Responsable: I3 e I4.
- Revisores: I1 e I2.
- Dependencias: T-0.3.
- Acción: aprobar tecnología, separación lógica o física y primer contrato de entrada/salida.
- Criterio de aceptación: frontend y backend pueden avanzar con mocks compatibles.
- Evidencia: arquitectura y contratos registrados en `2_spec.md`.

### [x] T-0.7 Definir estrategia Git

- Responsable: todo el equipo.
- Dependencias: T-0.1.
- Acción: acordar ramas, PR, revisiones y commits.
- Criterio de aceptación: existen rama de integración y cuatro ramas iniciales; el flujo está documentado.
- Evidencia: estrategia registrada en `2_spec.md`, estructura inicial y ramas publicadas en GitHub.

### [ ] T-0.8 Elegir herramienta organizativa

- Responsable: todo el equipo.
- Dependencias: T-0.1.
- Acción: elegir Trello u otra herramienta, crear el tablero y registrar el enlace.
- Criterio de aceptación: backlog visible y estados de trabajo acordados.
- Evidencia: enlace registrado en `2_spec.md` y README.

## Fase 1 — Base común y `Data Ready`

### [ ] T-1.1 Implementar conexión única al dataset

- Responsable: I1.
- Revisor: I4.
- Dependencias: T-0.2, T-0.3.
- Acción: crear un mecanismo reproducible para cargar el dataset canónico sin modificar el original.
- Criterio de aceptación: los cuatro integrantes pueden obtener la misma versión de datos.
- Verificación: comprobar schema, clases, dimensiones, resolución/representación elegidas y MD5 del archivo de Zenodo.

### [ ] T-1.2 Crear diccionario y auditoría de datos

- Responsable: I1.
- Revisor: I3.
- Dependencias: T-1.1.
- Acción: documentar columnas, tipos, target, identificadores, disponibilidad y riesgos.
- Criterio de aceptación: todas las variables tienen rol y descripción.
- Evidencia: diccionario de datos revisado.

### [ ] T-1.3 Realizar EDA compartido

- Responsable: todos; coordina I1.
- Dependencias: T-1.1, T-1.2.
- Acción: dividir preguntas de análisis entre los cuatro y consolidar un único EDA.
- Criterio de aceptación: nulos, duplicados, distribuciones, target, relaciones, correlaciones y leakage analizados.
- Evidencia: notebook o informe reproducible con interpretaciones.

### [ ] T-1.4 Implementar limpieza común

- Responsable: I1.
- Revisores: I2 e I4.
- Dependencias: T-1.3.
- Acción: codificar las reglas aprobadas sin alterar el dataset original.
- Criterio de aceptación: limpieza determinista, documentada y probada.
- Evidencia: tests y comparación antes/después.

### [ ] T-1.5 Congelar particiones comunes

- Responsable: I2.
- Revisor: I1.
- Dependencias: T-1.4, T-0.4.
- Acción: generar y versionar train, validación y test mediante el protocolo aprobado.
- Criterio de aceptación: los cuatro candidatos reciben los mismos registros.
- Evidencia: índices, metadata o función reproducible; test final protegido.

### [ ] T-1.6 Crear frontend simulado

- Responsable: I3.
- Revisor: I4.
- Dependencias: T-0.6, T-1.2.
- Acción: implementar o diseñar el flujo con respuestas mock según la arquitectura aprobada.
- Criterio de aceptación: formulario, resultado y error pueden demostrarse sin modelo definitivo.
- Evidencia: prueba visual o test de interfaz.

### [ ] T-1.7 Crear backend de inferencia simulado

- Responsable: I4.
- Revisor: I3.
- Dependencias: T-0.6, T-1.2.
- Acción: implementar o diseñar una entrada mock de imagen y una respuesta con letra, confianza, versión del modelo y errores controlados; definir límites de formato y tamaño sin descargar todavía el dataset completo.
- Criterio de aceptación: contrato consumible por frontend.
- Evidencia: prueba de contrato o llamada reproducible.

### [ ] T-1.8 Verificar gate `Data Ready`

- Responsable: todo el equipo; coordina I2.
- Dependencias: T-1.1 a T-1.7.
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

### [ ] T-2.6 Seleccionar y versionar Champion

- Responsable: todo el equipo; coordina I2.
- Dependencias: T-2.5.
- Acción: aplicar los criterios de selección y evaluar una vez el test final.
- Criterio de aceptación: Champion cumple overfitting, integración y métricas aprobadas.
- Evidencia: decisión, metadata, métricas finales y artefacto completo.

## Fase 3 — Integración y Nivel Esencial

### [ ] T-3.1 Validar pipeline Champion para inferencia

- Responsable: I1.
- Revisores: I2 e I4.
- Dependencias: T-2.6.
- Acción: comprobar schema, transformaciones y casos límite.
- Criterio de aceptación: entrenamiento e inferencia usan el mismo pipeline.

### [ ] T-3.2 Integrar Champion en backend

- Responsable: I4.
- Revisores: I1 e I2.
- Dependencias: T-2.6, T-1.7.
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
- Dependencias: T-2.6.
- Acción: documentar EDA, candidatos, Champion, métricas, overfitting, errores y limitaciones.
- Criterio de aceptación: cifras coherentes con artefactos y pruebas.

### [ ] T-3.6 Ejecutar smoke test esencial

- Responsable: I3 e I4.
- Revisores: I1 e I2.
- Dependencias: T-3.3, T-3.4.
- Acción: ejecutar flujo completo con casos válidos e inválidos.
- Criterio de aceptación: aplicación funcional y evidencia registrada.

### [ ] T-3.7 Verificar cierre del Nivel Esencial

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
