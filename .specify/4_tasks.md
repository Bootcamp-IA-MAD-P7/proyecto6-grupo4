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
| Alineación | En progreso | T-0.1: aprobar SDD reconciliado |
| Dataset técnico | Cerrado | Daily 22/07, ADR-0001, loader y manifest |
| Licencia | Bloqueado | T-0.2b: condiciones de uso y redistribución |
| Evaluación | Pendiente | T-0.4: métrica, gap y ventanas temporales |
| Aplicación | En progreso | T-0.6: arquitectura y contrato definitivo |
| `Data Ready` | Abierto | T-1.8 y checklist de `2_spec.md` |
| Nivel Esencial | No iniciado | Requiere `Data Ready` |

## Fase 0 — Decisiones bloqueantes

### [~] T-0.1 Revisar y aprobar `.specify/`

- Responsable: todo el equipo.
- Revisor: todo el equipo.
- Dependencias: ninguna.
- Requisitos: todos los `DEC`.
- Acción: leer `0_constitution.md` y los cuatro documentos SPEC, registrar dudas y aprobar o corregir el contrato.
- Criterio de aceptación: los cuatro integrantes aprueban dominio, gates, flujo común de datos, contratos y cuatro pipelines.
- Evidencia: aprobación fechada en daily o PR.

### [x] T-0.2a Evaluar y seleccionar técnicamente el dataset

- Responsable: I1, con aportes de I2, I3 e I4.
- Dependencias: ninguna; spike de decisión previo al SDD definitivo.
- Requisitos: DEC-01, DEC-03–DEC-06.
- Acción: evaluar target, tamaño, leakage, interpretabilidad, balance y viabilidad de aplicación.
- Criterio de aceptación: selección técnica, unidad partido, usuario y target explicables.
- Evidencia: daily 22/07/2026, `docs/decisions/0001-laliga-dataset-target-proposal.md`, EDA y manifest.

### [!] T-0.2b Confirmar condiciones de uso y redistribución

- Responsable: I1.
- Revisores: I2 e I4.
- Dependencias: T-0.2a.
- Requisito: DEC-02.
- Acción: confirmar términos aplicables a cada CSV, atribución y si puede versionarse o debe adquirirse mediante script/instrucciones.
- Criterio de aceptación: evidencia oficial enlazada y decisión `aprobada` en `2_spec.md`; si una fuente no es utilizable, se sustituye antes de entrenar.
- Evidencia actual: `reports/metrics/source_provenance.json`.
- Bloqueo: no se ha verificado una licencia abierta explícita para ambas fuentes.

### [x] T-0.3 Definir problema, usuarios y target

- Responsable: todo el equipo; coordina I1.
- Dependencias: T-0.2a.
- Requisitos: DEC-03–DEC-06.
- Acción: aprobar problema de negocio, usuario, unidad de predicción, target y clases.
- Criterio de aceptación: el equipo puede explicar qué se predice, para quién y con qué utilidad.
- Evidencia: daily 22/07/2026, `1_intent.md` y `2_spec.md`.

### [ ] T-0.4 Definir protocolo de evaluación

- Responsable: I2.
- Revisor: I1.
- Dependencias: T-0.3.
- Requisitos: DEC-07–DEC-09, ML-03, ML-04, ML-06.
- Acción: aprobar macro-F1 o alternativa justificada, métricas secundarias, ventanas temporales, baselines, semilla algorítmica y fórmula de overfitting.
- Criterio de aceptación: protocolo aprobado por los cuatro integrantes.
- Verificación: fixture temporal demuestra ausencia de solapamiento y que test no interviene en selección.
- Evidencia: contrato registrado en `2_spec.md` y artefacto de splits cuando corresponda.

### [ ] T-0.5 Elegir cuatro modelos candidatos

- Responsable: todo el equipo; coordina I2.
- Dependencias: T-0.3, T-0.4.
- Requisito: ML-02.
- Acción: asignar un algoritmo a cada integrante y justificar diversidad y viabilidad.
- Criterio de aceptación: candidatos A, B, C y D registrados sin duplicación injustificada.
- Evidencia: tabla de decisiones de `2_spec.md` actualizada.

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

### [~] T-1.2 Crear diccionario y auditoría de datos

- Responsable: I1.
- Revisor: I3.
- Dependencias: T-1.1.
- Requisito: ML-01.
- Acción: documentar columnas, tipos, target, identificadores, disponibilidad y riesgos.
- Criterio de aceptación: todas las variables tienen rol y descripción.
- Evidencia: diccionario de datos revisado.
- Evidencia provisional: `reports/metrics/data_dictionary.csv`, `reports/metrics/missingness.csv` y `reports/metrics/eda_summary.json`. Pendiente revisión de I3.

### [~] T-1.3 Realizar EDA compartido

- Responsable: todos; coordina I1.
- Dependencias: T-1.1, T-1.2.
- Requisitos: ML-01, ML-06.
- Acción: dividir preguntas de análisis entre los cuatro y consolidar un único EDA.
- Criterio de aceptación: nulos, duplicados, distribuciones, target, relaciones, correlaciones y leakage analizados.
- Evidencia: notebook o informe reproducible con interpretaciones.
- Evidencia provisional: `notebooks/01_laliga_eda.ipynb`, `reports/laliga_eda.md` y once figuras persistentes en `reports/figures/`, incluidas outliers y dos matrices de confusión descriptivas. Análisis técnico completo; pendiente revisión cruzada de los cuatro integrantes.

### [~] T-1.4 Implementar limpieza común

- Responsable: I1.
- Revisores: I2 e I4.
- Dependencias: T-1.3.
- Requisito: ML-01.
- Acción: codificar las reglas aprobadas sin alterar el dataset original.
- Criterio de aceptación: limpieza determinista, documentada y probada.
- Evidencia: tests y comparación antes/después.
- Evidencia provisional 2026-07-23: `notebooks/00_laliga_preprocessing.ipynb`, `data/processed/laliga_matches_clean.csv`, `reports/metrics/preprocessing_summary.json`, `reports/metrics/source_column_policy.csv` y pruebas unitarias/integración. Pendientes revisión de I2/I4 y cierre de dependencias.

### [ ] T-1.5 Implementar features comunes y congelar particiones temporales

- Responsables: I1 e I2.
- Revisores: I3 e I4.
- Dependencias: T-1.4, T-0.4.
- Requisitos: DEC-07, ML-01, ML-04.
- Acción: implementar el generador común de features históricas con `shift(1)` y generar train, validación y test cronológicos mediante el protocolo aprobado.
- Criterio de aceptación: los cuatro candidatos reciben las mismas columnas y registros; ninguna feature usa el partido actual o futuro.
- Verificación: tests de causalidad temporal, schema, ausencia de solapamiento y test final protegido.
- Evidencia: generador, índices o metadata, versión y SHA-256.

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
| Estado | v1.0 — dependencias, spikes, gates y trazabilidad reconciliados |
| Fecha | 23/07/2026 |
| Siguiente trabajo bloqueante | T-0.1, T-0.2b, T-0.4, T-0.5 y T-0.6 |
| Regla | Marcar `[x]` solo con verificación, evidencia y revisión cruzada |
