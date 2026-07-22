# SPEC 2 — Especificación técnica

## Autoridad y estado

Este documento define el contrato técnico del proyecto. Toda implementación debe respetarlo o detenerse hasta que el equipo apruebe y documente un cambio.

Estado actual: **definición inicial; implementación bloqueada por decisiones pendientes**.

## Requisitos obligatorios de la consigna

### Entregables

- Aplicación que reciba datos y devuelva una predicción de clasificación.
- Repositorio en GitHub con ramas ordenadas y mensajes de commit limpios.
- Informe técnico del rendimiento y explicación del modelo.
- Presentación orientada a negocio.
- Presentación técnica del código.
- Enlace a Trello u otra herramienta organizativa.

### Tecnologías indicadas

- Scikit-learn.
- Pandas.
- Streamlit, Dash o Gradio como tecnologías de interfaz indicadas por la consigna.
- Git y GitHub.
- Docker.

La consigna también menciona una API como posible mecanismo de productivización. La tecnología definitiva de aplicación deberá aprobarse antes de implementarse.

### Restricción de overfitting

El modelo productivizado deberá demostrar una diferencia inferior al 5 % entre entrenamiento y validación, calculada sobre la métrica que el equipo apruebe.

Pendiente de decisión:

- Métrica utilizada para calcular el gap.
- Diferencia absoluta, relativa o en puntos porcentuales.
- Tratamiento de variaciones entre folds.

Hasta resolver estas decisiones ningún modelo podrá declararse Champion.

## Requisitos acumulativos por nivel

### Nivel Esencial

- Modelo funcional de clasificación.
- EDA con visualizaciones relevantes.
- Overfitting inferior al 5 %.
- Solución productivizada.
- Informe con métricas de clasificación, explicación del rendimiento, importancia de variables o equivalente y análisis de errores.

### Nivel Medio

- Modelo ensemble.
- Validación cruzada.
- Optimización de hiperparámetros.
- Recogida de feedback.
- Recogida de datos nuevos para futuros reentrenamientos.

### Nivel Avanzado

- Dockerización.
- Persistencia en base de datos de los datos recogidos.
- Despliegue.
- Tests unitarios.

### Nivel Experto

- Experimento o despliegue de red neuronal.
- A/B testing.
- Monitorización de data drift.
- Reemplazo de modelo condicionado por métricas predefinidas.

Docker aparece también en la lista general de tecnologías. Por esta ambigüedad, la compatibilidad con Docker se comprobará temprano, aunque el gate formal de dockerización pertenezca al Nivel Avanzado. La interpretación definitiva deberá confirmarse con el equipo o el personal docente.

## Estado de decisiones técnicas

| Decisión | Estado | Valor |
|---|---|---|
| Dataset | Pendiente | No seleccionado |
| Problema de negocio | Pendiente | No definido |
| Usuario principal | Pendiente | No definido |
| Target | Pendiente | No definido |
| Tipo de clasificación | Pendiente | Binaria o multiclase |
| Métrica principal | Pendiente | No definida |
| Fórmula de overfitting | Pendiente | Debe demostrar gap menor al 5 % |
| Modelos A, B, C y D | Pendiente | No seleccionados |
| Tecnología frontend | Pendiente | No seleccionada |
| Tecnología backend | Pendiente | No seleccionada |
| Persistencia | Pendiente | No seleccionada |
| Despliegue | Pendiente | No seleccionado |
| Gestión del equipo | Pendiente | Trello u otra herramienta |
| Estrategia Git | Aprobada | `main` estable, `develop` integración y ramas `feature/` por ticket |

## Estrategia Git aprobada

### Ramas permanentes

- `main`: versión estable, demostrable y potencialmente entregable.
- `develop`: rama de integración del trabajo revisado.

No se trabajará directamente sobre estas ramas salvo una operación de bootstrap aprobada por el equipo. El cambio que crea la estructura inicial constituye esa operación excepcional.

### Ramas de trabajo

Las ramas de trabajo serán temporales y estarán asociadas a un ticket de `4_tasks.md`.

Formato general:

```text
feature/t-<fase>.<tarea>-<descripcion-corta>
```

Ejemplos posteriores:

```text
feature/t-1.1-dataset-loader
feature/t-2.1-model-a
feature/t-3.3-frontend-integration
```

Para iniciar los cuatro frentes se crean estas ramas:

- `feature/i1-data-foundation`.
- `feature/i2-evaluation-contract`.
- `feature/i3-frontend-mock`.
- `feature/i4-backend-mock`.

Estas ramas iniciales no son ramas personales permanentes. Se cerrarán después de integrar las tareas iniciales y las siguientes ramas se crearán por ticket.

### Flujo de integración

1. Actualizar la rama de trabajo desde `develop` antes de comenzar.
2. Implementar únicamente el ticket asignado.
3. Ejecutar pruebas y registrar evidencia.
4. Abrir Pull Request hacia `develop`.
5. Obtener al menos una revisión de otra persona.
6. Integrar solo con criterios de aceptación satisfechos.
7. Eliminar la rama temporal después del merge.
8. Promover `develop` a `main` mediante Pull Request cuando exista un gate estable.

No se permiten pushes directos a `main` ni a `develop` después del bootstrap. Los cambios urgentes deberán utilizar una rama temporal y revisión.

### Convención de commits

Los commits serán pequeños y descriptivos. Prefijos recomendados:

- `feat:` funcionalidad.
- `fix:` corrección.
- `docs:` documentación.
- `test:` pruebas.
- `refactor:` reestructuración sin cambio funcional.
- `chore:` mantenimiento.

## Estructura objetivo del repositorio

La estructura inicial es neutral respecto del dataset, los cuatro algoritmos y los frameworks de frontend/backend:

```text
.
|-- .github/
|   |-- workflows/
|   `-- pull_request_template.md
|-- .specify/
|   |-- 1_intent.md
|   |-- 2_spec.md
|   |-- 3_plan.md
|   `-- 4_tasks.md
|-- app/
|   |-- backend/
|   `-- frontend/
|-- config/
|-- data/
|   |-- raw/
|   |-- interim/
|   |-- processed/
|   `-- feedback/
|-- docker/
|-- docs/
|   |-- business_presentation/
|   |-- decisions/
|   |-- project_management/
|   `-- technical_presentation/
|-- models/
|   |-- candidates/
|   |   |-- model_a/
|   |   |-- model_b/
|   |   |-- model_c/
|   |   `-- model_d/
|   |-- champion/
|   `-- monitoring/
|-- notebooks/
|-- reports/
|   |-- experiments/
|   |-- figures/
|   `-- metrics/
|-- scripts/
|-- src/
|   |-- candidates/
|   |   |-- model_a/
|   |   |-- model_b/
|   |   |-- model_c/
|   |   `-- model_d/
|   |-- common/
|   |-- data/
|   |-- evaluation/
|   |-- inference/
|   `-- mlops/
|-- tests/
|   |-- e2e/
|   |-- fixtures/
|   |-- integration/
|   `-- unit/
|-- .gitignore
`-- README.md
```

Responsabilidades de las áreas principales:

- `data/raw/`: dataset original inmutable; inicialmente ignorado por Git salvo marcador.
- `data/interim/`: resultados intermedios reproducibles.
- `data/processed/`: base común posterior a las reglas aprobadas.
- `src/data/`: conexión, auditoría y limpieza comunes.
- `src/candidates/model_*`: pipeline y entrenamiento específicos de cada candidato.
- `models/candidates/model_*`: artefactos candidatos; inicialmente ignorados por Git salvo marcador.
- `src/evaluation/`: métricas, overfitting y comparación común.
- `app/frontend/` y `app/backend/`: separación lógica preparada sin imponer frameworks.
- `src/inference/`: carga del Champion y lógica de inferencia compartida.
- `src/mlops/` y `models/monitoring/`: componentes opcionales de niveles superiores.
- `reports/`: evidencia generada, métricas, experimentos y figuras.
- `tests/`: pruebas separadas por alcance.

No se crearán implementaciones dentro de estas carpetas hasta que exista un ticket autorizado y se hayan resuelto sus decisiones técnicas.

## Estrategia común de datos

### Dataset canónico

El equipo seleccionará un único dataset. Su carga se implementará una sola vez y será reutilizada por los cuatro integrantes.

El dataset original deberá:

- Mantenerse inmutable.
- Tener una fuente y licencia documentadas.
- Tener una variable objetivo categórica clara.
- Permitir una decisión o historia de negocio comprensible.
- Ser suficiente para separar entrenamiento, validación y test.
- Evitar datos sensibles innecesarios.
- Permitir una aplicación con inputs disponibles antes de la predicción.

No se crearán cuatro mecanismos independientes de conexión o cuatro versiones incompatibles del dataset.

### EDA y limpieza comunes

Se realizará una única fase compartida de EDA y limpieza inicial. Todos los integrantes contribuirán al análisis; el Integrante 1 coordinará la consolidación técnica.

El EDA deberá cubrir como mínimo:

- Dimensiones y tipos.
- Nulos y duplicados.
- Distribución del target.
- Posible desbalance.
- Distribuciones de variables.
- Valores extremos.
- Relaciones con el target.
- Correlaciones cuando sean pertinentes.
- Identificadores sin valor predictivo.
- Variables posteriores al evento o con leakage.
- Viabilidad de convertir variables en entradas de aplicación.

Las reglas comunes de limpieza deberán quedar codificadas y documentadas. Ningún integrante podrá limpiar o eliminar observaciones de forma diferente para favorecer su modelo.

Se permiten diagnósticos adicionales específicos por modelo, siempre que no alteren la base común sin aprobación.

### Preprocesamiento común y separación de responsabilidades

El Integrante 1 mantendrá una capa común y reutilizable para validar el contrato, aplicar exclusiones y ejecutar las reglas de limpieza aprobadas. Esta capa deberá prevenir data leakage, quedar sin ajustar hasta disponer de las particiones congeladas y garantizar que cualquier transformación con estado se ajuste únicamente sobre entrenamiento. El mismo componente ajustado deberá reutilizarse sin divergencias durante la inferencia.

El preprocesamiento común no elimina la responsabilidad de cada integrante sobre su pipeline candidato. La imputación, codificación, escalado, selección o balanceo específicos de un algoritmo permanecerán encapsulados en el pipeline de ese candidato. El Pipeline A consumirá la capa común y añadirá únicamente sus transformaciones específicas.

Frontend y backend no duplicarán transformaciones estadísticas. El backend deberá invocar el pipeline serializado que corresponda y el frontend se limitará a validaciones de interacción compatibles con el contrato de entrada.

### Contrato de datos

Antes de entrenar deberá documentarse para cada variable:

- Nombre técnico.
- Descripción.
- Tipo.
- Rol: feature, target, identificador o excluida.
- Valores o rango permitidos y categorías admitidas cuando corresponda.
- Obligatoriedad.
- Tratamiento común de nulos.
- Disponibilidad en el momento de inferencia.
- Riesgo de leakage o sensibilidad.

El contrato incluirá ejemplos de entradas válidas e inválidas que frontend y backend puedan reutilizar en desarrollo y pruebas.

### Particiones congeladas

Las particiones de entrenamiento, validación y test se generarán una sola vez y serán utilizadas por los cuatro candidatos.

Requisitos:

- Semilla reproducible.
- Estratificación cuando resulte apropiada.
- Índices o mecanismo de generación versionados.
- Test final reservado.
- Transformaciones ajustadas únicamente con entrenamiento.

El Integrante 2 coordinará este contrato con revisión del Integrante 1.

### Gate `Data Ready`

No podrá comenzar el entrenamiento individual hasta verificar:

- [ ] Dataset seleccionado y accesible.
- [ ] Fuente y licencia documentadas.
- [ ] Target y clases aprobados.
- [ ] EDA inicial completado.
- [ ] Reglas comunes de limpieza aprobadas.
- [ ] Variables con leakage excluidas.
- [ ] Contrato de datos aprobado.
- [ ] Particiones comunes reproducibles.
- [ ] Test final protegido.
- [ ] Métricas comunes definidas.
- [ ] Fórmula de overfitting definida.
- [ ] Cuatro modelos candidatos aprobados.

## Pipelines individuales

Cada integrante desarrollará un pipeline completo orientado a su modelo:

- Integrante 1: Pipeline A + Modelo A.
- Integrante 2: Pipeline B + Modelo B.
- Integrante 3: Pipeline C + Modelo C.
- Integrante 4: Pipeline D + Modelo D.

Los pipelines podrán diferir en:

- Imputación específica.
- Codificación.
- Escalado.
- Selección de variables.
- Transformaciones matemáticas.
- Balanceo aplicado solo sobre entrenamiento.
- Hiperparámetros y estimador.

Todos deberán:

- Consumir el mismo contrato de datos.
- Usar las mismas particiones.
- Respetar las exclusiones comunes.
- Encapsular las transformaciones necesarias para inferencia.
- Ajustar transformaciones solo con entrenamiento.
- Ser reproducibles.
- Guardar el pipeline completo junto con el estimador.
- Producir predicciones en un formato comparable.
- Ser compatibles con el contrato de aplicación aprobado.

Queda prohibido modificar el dataset canónico, el target o los splits desde un pipeline individual.

## Contrato común de experimentación

Cada experimento deberá registrar:

- Identificador del candidato.
- Integrante responsable.
- Versión de datos.
- Features utilizadas.
- Transformaciones.
- Algoritmo.
- Hiperparámetros.
- Semilla.
- Métricas de entrenamiento.
- Métricas de validación.
- Gap de overfitting.
- Matriz de confusión.
- Curva ROC o alternativa cuando aplique.
- Tiempo de entrenamiento.
- Tiempo de inferencia cuando sea relevante.
- Limitaciones y errores observados.
- Resultado de validación cruzada cuando corresponda.

La comparación solo será válida si los cuatro candidatos respetan este contrato.

## Selección del Champion

El equipo seleccionará el pipeline más modelo que se productivizará. Ningún integrante podrá promocionar unilateralmente su candidato.

El Champion deberá:

- Cumplir el overfitting inferior al 5 %.
- Superar una referencia mínima o justificar su selección.
- Mantener un rendimiento aceptable en métricas secundarias.
- Incluir análisis de errores.
- Ser reproducible y serializable.
- Poder cargarse desde la aplicación.
- Mantener el mismo contrato de entrada.
- Tener versión y metadata.

Cuando dos candidatos tengan rendimiento semejante se priorizará, en este orden sujeto a aprobación:

1. Mejor generalización.
2. Menor complejidad operativa.
3. Mayor interpretabilidad.
4. Menor coste de inferencia.

El test final se utilizará una única vez después de la selección y no se reutilizará para tuning.

## Distribución técnica y contratos

### Integrante 1 — Datos y ciclo de vida del dato

- Audita el dataset aprobado: tipos, nulos, duplicados, valores extremos, clases y posibles fugas de información.
- Coordina la consolidación del EDA compartido y mantiene el diccionario y contrato de datos, incluidos tipo, rango, categorías y obligatoriedad.
- Acuerda con el Integrante 2 la estrategia de partición y con los Integrantes 3 y 4 los contratos de entrada.
- Construye y mantiene el preprocesamiento común según la separación de responsabilidades definida en esta especificación.
- Entrena Pipeline A + Modelo A y registra parámetros, tiempos, métricas y overfitting.
- Proporciona casos de datos válidos e inválidos para frontend, backend y pruebas.
- Valida la coherencia entre entrenamiento e inferencia, incluidas categorías desconocidas, nulos, límites y entradas incorrectas.
- Valida la calidad de los datos de feedback y mantiene la referencia estadística de drift cuando corresponda.
- Documenta transformaciones, exclusiones y limitaciones durante todo el ciclo de vida.

El Integrante 1 no podrá cambiar particiones sin aprobación del Integrante 2 y del equipo, seleccionar unilateralmente el Champion, duplicar preprocesamiento en frontend ni modificar frontend o backend salvo autorización expresa de una tarea.

### Integrante 2 — Evaluación y ciclo de vida del modelo

- Coordina splits, métricas, overfitting y comparación.
- Entrena Pipeline B + Modelo B.
- Mantiene la tabla de experimentos.
- Coordina selección, análisis de errores y pruebas de regresión.

### Integrante 3 — Frontend y producto

- Define el flujo de usuario y frontend con contratos simulados desde el inicio.
- Entrena Pipeline C + Modelo C.
- Implementa formularios, resultados, errores y feedback visual.
- Prueba la experiencia de usuario y prepara la demostración de negocio.

### Integrante 4 — Backend, integración y despliegue

- Define el servicio de inferencia con contratos simulados desde el inicio.
- Entrena Pipeline D + Modelo D.
- Integra Champion, persistencia, Docker y despliegue.
- Coordina pruebas de API, integración, contenedor y ejecución.

## Contrato de aplicación

La aplicación deberá ofrecer, como mínimo:

- Inputs equivalentes al contrato del Champion.
- Validación de tipos y valores.
- Ejecución del mismo pipeline usado durante entrenamiento.
- Clase predicha.
- Probabilidad o confianza cuando aplique.
- Mensaje comprensible y no causal.
- Tratamiento controlado de errores.

El contrato concreto deberá definirse después del `Data Ready` e incluir:

- Schema de entrada.
- Schema de salida.
- Manejo de errores.
- Versión del modelo.
- Mecanismo de feedback si se alcanza el Nivel Medio.
- Ejemplos de entradas válidas e inválidas mantenidos junto con el contrato de datos.

El frontend no realizará transformaciones estadísticas propias del pipeline.

## Testing distribuido

- Integrante 1: tests de carga, contrato de datos, transformaciones comunes, categorías desconocidas, nulos, límites y entradas incorrectas.
- Integrante 2: tests de métricas, overfitting, comparación y regresión.
- Integrante 3: tests de interfaz y flujo de usuario.
- Integrante 4: tests de backend, integración, serialización, Docker y despliegue.

Cada integrante probará además su pipeline y modelo candidato. El autor de un componente no será su único revisor.

## Definición de terminado

Una tarea solo se considerará terminada cuando:

- Cumpla sus dependencias.
- Respete los contratos de esta especificación.
- Tenga código o documento completo.
- Tenga pruebas proporcionales al riesgo.
- Registre comandos y resultados de verificación.
- Actualice la documentación afectada.
- No rompa el Nivel Esencial.
- Tenga la revisión cruzada indicada en `4_tasks.md`.
- Disponga de evidencia reproducible.

## Seguridad y privacidad

- No se guardarán secretos en Git.
- No se registrarán credenciales en logs.
- No se utilizarán datos personales sensibles sin necesidad y justificación.
- Las predicciones no se presentarán como certezas.
- La importancia de variables no se presentará como causalidad.
- Un sistema de drift nunca promoverá por sí solo un modelo.

## Control de cambios

Cambios sobre dataset, target, limpieza, splits, métricas, overfitting, contratos o arquitectura requieren:

1. Propuesta explícita.
2. Revisión de las personas afectadas.
3. Aprobación del equipo.
4. Actualización de `.specify/`.
5. Reevaluación de candidatos si se pierde comparabilidad.
