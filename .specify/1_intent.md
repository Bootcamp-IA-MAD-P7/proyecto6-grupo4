# SPEC 1 — Intención del proyecto

## Propósito

Construir en equipo una solución de machine learning para un problema de clasificación supervisada. La solución deberá analizar un conjunto de datos, entrenar y comparar cuatro modelos candidatos, seleccionar un modelo final con evidencia reproducible y productivizarlo en una aplicación que reciba datos y devuelva una predicción comprensible.

El equipo está formado por cuatro integrantes con nivel técnico semejante y dispone de ocho días hábiles. Los cuatro integrantes actuarán como developers durante todo el proyecto: escribirán código, entrenarán un candidato, probarán componentes, documentarán resultados y participarán en la integración.

## Fuente central de verdad

La carpeta `.specify/` constituye el contrato común del proyecto y debe leerse antes de proponer o modificar código.

Sus documentos cumplen estas funciones:

- `1_intent.md`: propósito, problema, alcance y principios.
- `2_spec.md`: requisitos, restricciones, contratos y criterios de aceptación.
- `3_plan.md`: estrategia de ejecución, fases, dependencias y gates.
- `4_tasks.md`: backlog ejecutable, responsables, revisiones y evidencias.

Si una decisión, tarea o implementación contradice estos documentos, el equipo deberá detenerse, resolver la contradicción y actualizar la especificación de forma explícita antes de continuar.

## Objetivo protegido: Nivel Esencial

La prioridad es entregar un Nivel Esencial estable. Debe existir, como mínimo:

- Un dataset de clasificación seleccionado, accesible y documentado.
- Una variable objetivo definida.
- Un EDA con visualizaciones relevantes.
- Reglas comunes de limpieza reproducibles.
- Cuatro pipelines y cuatro modelos candidatos comparables.
- Un modelo final seleccionado con métricas de clasificación.
- Evidencia de overfitting inferior al 5 % según la fórmula aprobada.
- Una aplicación que reciba datos y devuelva una predicción.
- Un informe técnico con métricas, interpretación y análisis de errores.
- Un repositorio ordenado y documentación de ejecución.

Ningún requisito de niveles superiores podrá bloquear o desestabilizar este núcleo.

## Evolución acumulativa

Los niveles se trabajarán en este orden:

1. Nivel Esencial.
2. Nivel Medio.
3. Nivel Avanzado.
4. Nivel Experto.

Un nivel solo podrá iniciarse cuando el anterior tenga sus criterios de cierre definidos, comprobados y registrados. Los niveles superiores son incrementos sobre una solución estable, no sustitutos del Nivel Esencial.

## Estrategia de datos y modelos aprobada

El equipo ha acordado el siguiente flujo:

1. Seleccionar un único dataset y crear una única conexión o mecanismo común de carga.
2. Realizar una única fase compartida de EDA inicial, limpieza y definición del contrato de datos.
3. Congelar una versión común de los datos y unas particiones comunes de entrenamiento, validación y test.
4. Desarrollar cuatro pipelines específicos, cada uno orientado al modelo de un integrante.
5. Entrenar cuatro modelos candidatos en paralelo.
6. Compararlos mediante el mismo protocolo y seleccionar el pipeline más modelo que se productivizará.

Cada pipeline podrá aplicar transformaciones específicas, pero no podrá redefinir unilateralmente el dataset, el target, las reglas comunes de limpieza o las particiones.

## Distribución técnica aprobada

- Integrante 1: Developer de datos y ciclo de vida del dato + Pipeline A + Modelo A.
- Integrante 2: Developer de evaluación y ciclo de vida del modelo + Pipeline B + Modelo B.
- Integrante 3: Developer de frontend y producto + Pipeline C + Modelo C.
- Integrante 4: Developer de backend, integración y despliegue + Pipeline D + Modelo D.

Ser responsable de un área significa garantizar su resultado y coordinar sus contratos; no significa trabajar en aislamiento. Testing, documentación, integración y defensa son responsabilidades compartidas.

## Producto esperado

La solución deberá permitir que un usuario introduzca datos compatibles con el modelo y reciba una clasificación. La interfaz concreta, el dominio, el dataset, el target y la arquitectura definitiva permanecen pendientes de aprobación.

La separación entre frontend y backend deberá existir al menos de forma lógica:

- El frontend gestiona interacción, formularios, validaciones visuales, resultados y feedback.
- El backend gestiona validación técnica, preprocesamiento, carga del modelo, inferencia, persistencia y respuesta.

La decisión de construir servicios separados o una única aplicación modular deberá registrarse en `2_spec.md` antes de implementarse.

## Principios de trabajo

- Priorizar una solución completa y demostrable antes de añadir complejidad.
- Mantener el dataset original inmutable.
- Evitar data leakage.
- Proteger el conjunto de test final.
- No comparar modelos entrenados con datos o métricas diferentes.
- Empezar frontend y backend con contratos simulados para reducir esperas.
- Integrar de forma progresiva.
- Probar cada componente antes de considerarlo terminado.
- Mantener evidencias reproducibles de decisiones y resultados.
- No introducir secretos ni datos sensibles innecesarios.
- No modificar componentes ajenos sin coordinación.

## Decisiones todavía pendientes

Antes de implementar componentes dependientes de ellas, el equipo deberá aprobar:

- Dataset y licencia o fuente de uso.
- Problema de negocio y usuarios.
- Variable objetivo y clases.
- Clasificación binaria o multiclase.
- Métrica principal y métricas secundarias.
- Fórmula operativa del overfitting inferior al 5 %.
- Estrategia de partición y semilla.
- Cuatro algoritmos candidatos.
- Tecnología y arquitectura de la aplicación.
- Estrategia de persistencia.
- Plataforma de despliegue.
- Estrategia Git, ramas y Pull Requests.
- Herramienta de organización del equipo.
- Nivel de entrega comprometido más allá del Nivel Esencial.

## Estado deseado al finalizar

Una persona ajena al desarrollo deberá poder:

- Entender qué problema se resuelve y para quién.
- Obtener o localizar el dataset.
- Reproducir la preparación de datos.
- Consultar los cuatro experimentos.
- Comprender por qué se seleccionó el modelo final.
- Ejecutar la aplicación y obtener una predicción.
- Ejecutar las pruebas documentadas.
- Revisar métricas, overfitting, errores y limitaciones.
- Identificar con claridad qué niveles se alcanzaron realmente.
