# Constitución del proyecto — Clasificación prepartido de LaLiga

## 1. Autoridad y precedencia

Este documento contiene las reglas estables y no negociables del proyecto. La fuente de verdad se interpreta en este orden:

1. `0_constitution.md`: principios y restricciones invariantes.
2. `1_intent.md`: producto, usuario, alcance y criterios de éxito.
3. `2_spec.md`: requisitos, contratos y decisiones técnicas vigentes.
4. `3_plan.md`: secuencia, dependencias, riesgos y calendario.
5. `4_tasks.md`: backlog ejecutable, responsables, revisiones y evidencias.

Si dos documentos discrepan, se detiene el trabajo afectado y se corrige primero el documento de mayor autoridad. El código, los notebooks, las dailys y el README no pueden redefinir por sí solos una decisión de `.specify/`.

## 2. Producto protegido

El Nivel Esencial es una aplicación de clasificación multiclase que estima, antes del inicio, el resultado final de un partido de Primera División:

- `H`: victoria del equipo local.
- `D`: empate.
- `A`: victoria del equipo visitante.

La predicción es orientativa y analítica. No se presenta como certeza, recomendación de apuesta ni relación causal.

## 3. Datos y ausencia de leakage

- Los dos CSV originales permanecen inmutables y con huellas verificables.
- La selección técnica de LaLiga, la unidad partido y `result_ft` están aprobadas por el equipo.
- La validación de las condiciones de uso y redistribución de las fuentes continúa siendo un gate independiente y bloqueante para cerrar `Data Ready`.
- Ningún candidato puede usar información generada durante o después del partido que intenta predecir.
- Las features de forma, fuerza, puntos, goles, Elo o enfrentamientos se calculan exclusivamente con partidos anteriores mediante operaciones cerradas al pasado.
- Los cuatro candidatos usan la misma versión del dataset, el mismo generador de features y las mismas particiones.
- La separación de entrenamiento, validación y test es temporal. Un split aleatorio por filas no es válido para la evaluación principal.
- El test final permanece reservado hasta seleccionar el Champion.

## 4. Comparabilidad y evaluación

- La métrica principal, las métricas secundarias y la fórmula de overfitting se aprueban antes del entrenamiento.
- El gap de overfitting se expresa en puntos absolutos de la métrica principal, no como porcentaje relativo ambiguo.
- Ningún resultado se compara si cambia unilateralmente datos, target, ventana temporal o evaluación.
- Las reglas descriptivas del EDA y las baselines no cuentan como modelos candidatos.
- El Champion se decide en equipo y debe ser reproducible, serializable e integrable.

## 5. Ejecución y revisión

- Solo se implementan tareas registradas en `4_tasks.md`.
- Una tarea no comienza con dependencias incumplidas, salvo que el backlog la identifique expresamente como spike exploratorio autorizado.
- Una tarea no se marca `[x]` sin criterio de aceptación, verificación reproducible, evidencia y revisión cruzada.
- Los cambios se realizan en ramas de trabajo y llegan a `develop` mediante Pull Request.
- Dataset, target, features comunes, splits, métricas, contratos de aplicación y arquitectura requieren actualización previa de `.specify/`.

## 6. Seguridad y uso responsable

- No se guardan secretos, tokens ni credenciales reales en Git, documentación o logs.
- No se incorporan datos personales o sensibles innecesarios.
- Las predicciones muestran incertidumbre y limitaciones.
- La importancia de variables no se interpreta como causalidad.

## 7. Alcance temporal

La entrega está planificada para el 30/07/2026. Se protege primero un Nivel Esencial completo y demostrable. Los niveles Medio, Avanzado y Experto solo se inician cuando el gate anterior está cerrado y no ponen en riesgo la entrega.

## 8. Estado del documento

| Campo | Valor |
|---|---|
| Estado | v1.0 aprobada por I1–I4 |
| Fecha | 24/07/2026 |
| Propietario | Todo el equipo |
| Evidencia | Daily 24/07/2026 y acta T-0.1 |
