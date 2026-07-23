# SPEC 1 — Intención del proyecto

> **Metodología SDD:** este documento define el qué y el porqué. Está gobernado por `0_constitution.md`; los requisitos verificables, el diseño de ejecución y el backlog viven en `2_spec.md`, `3_plan.md` y `4_tasks.md`.

## Propósito

Construir en equipo una solución de machine learning para un problema de clasificación supervisada. La solución deberá analizar un conjunto de datos, entrenar y comparar cuatro modelos candidatos, seleccionar un modelo final con evidencia reproducible y productivizarlo en una aplicación que reciba datos y devuelva una predicción comprensible.

El equipo está formado por cuatro integrantes con nivel técnico semejante y dispone de ocho días hábiles. Los cuatro integrantes actuarán como developers durante todo el proyecto: escribirán código, entrenarán un candidato, probarán componentes, documentarán resultados y participarán en la integración.

## Fuente central de verdad

La carpeta `.specify/` constituye el contrato común del proyecto y debe leerse antes de proponer o modificar código.

Sus documentos cumplen estas funciones:

- `0_constitution.md`: reglas invariantes, precedencia y control de cambios.
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

El producto es una aplicación de análisis deportivo que estima, antes del inicio de un partido de LaLiga, si el resultado final será victoria local (`H`), empate (`D`) o victoria visitante (`A`).

La persona usuaria principal es alguien interesado en análisis deportivo prepartido. Introducirá o seleccionará los equipos y la fecha del encuentro; la aplicación devolverá la clase estimada, las probabilidades de `H`, `D` y `A`, la versión del modelo y un mensaje comprensible sobre la incertidumbre.

Las features históricas se calcularán en backend a partir de partidos anteriores. El usuario no introducirá goles, tiros, faltas, córners, tarjetas ni ninguna información del partido actual que todavía no exista en el momento de inferencia.

La separación entre frontend y backend deberá existir al menos de forma lógica:

- El frontend gestiona interacción, formularios, validaciones visuales, resultados y feedback.
- El backend gestiona validación técnica, preprocesamiento, carga del modelo, inferencia, persistencia y respuesta.

La decisión de construir servicios separados o una única aplicación modular deberá registrarse en `2_spec.md` antes de implementarse.

## Dominio y target aprobados — LaLiga

Fecha de decisión del equipo: 2026-07-22.

El dataset de trabajo combina partidos de LaLiga 1995-96–2025-26. La unidad de análisis es un partido y el target es `result_ft`, con tres clases: `H` (victoria local), `D` (empate) y `A` (victoria visitante).

El problema aprobado es estimar antes del inicio el resultado final. Los únicos inputs admisibles son datos disponibles en ese momento. Marcadores, tiros, faltas, córners, tarjetas y cualquier variable derivada del encuentro actual se consideran posteriores al evento y quedan excluidos por leakage.

La selección técnica, el problema y el target constan como aprobados en la daily del 22/07/2026. La validación de las condiciones de uso y redistribución de las fuentes sigue pendiente y bloquea el cierre de `Data Ready`. También permanecen pendientes el protocolo de evaluación, los cuatro candidatos y la arquitectura definitiva.

## Alcance del MVP

Incluye:

- Carga y preparación reproducibles del histórico.
- Features comunes calculadas únicamente con información anterior a cada partido.
- Cuatro modelos candidatos comparables.
- Selección de un Champion mediante validación temporal.
- Aplicación con formulario prepartido y probabilidades por clase.
- API o backend con validación, inferencia y versionado.
- Informe técnico, análisis de errores y pruebas esenciales.

## Fuera de alcance del MVP

- Predicción en directo una vez iniciado el partido.
- Uso de estadísticas del encuentro actual.
- Recomendaciones de apuestas o promesas de rentabilidad.
- Integración obligatoria con proveedores de cuotas.
- Reentrenamiento automático, A/B testing o drift antes de cerrar el Nivel Esencial.
- Interpretaciones causales de las variables.

## Criterios de éxito del producto

El MVP será satisfactorio cuando:

- Un usuario pueda seleccionar un partido válido y obtener `H`, `D` o `A` con probabilidades y versión del modelo.
- El pipeline de features demuestre que solo usa partidos anteriores.
- Los cuatro candidatos se evalúen con la misma partición temporal y el mismo protocolo.
- El Champion supere la baseline aprobada en la métrica principal y cumpla el gap de overfitting.
- El flujo completo pueda reproducirse desde un clon limpio mediante instrucciones documentadas.
- Los errores de entrada y categorías no conocidas se traten de forma controlada.

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

- Condiciones de uso y redistribución de las dos fuentes.
- Métrica principal y métricas secundarias.
- Fórmula operativa del overfitting inferior al 5 %.
- Ventanas temporales exactas de train, validación y test.
- Contrato definitivo de features históricas.
- Cuatro algoritmos candidatos.
- Tecnología y arquitectura de la aplicación.
- Estrategia de persistencia.
- Plataforma de despliegue.
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

## Estado del documento

| Campo | Valor |
|---|---|
| Estado | v1.0 — dominio, usuario, target y alcance reconciliados |
| Fecha | 23/07/2026 |
| Evidencia de decisión | `docs/project_management/Dailys1.md`, daily 22/07/2026 |
| Pendiente | Aprobación formal de T-0.1 y decisiones listadas arriba |
