# ADR 0001 — Propuesta de dataset y target de LaLiga

- Estado: propuesta pendiente de aprobación cruzada.
- Fecha: 2026-07-22.
- Tareas relacionadas: T-0.2, T-0.3, T-1.1, T-1.2 y T-1.3.

## Contexto

El proyecto necesita un único dataset de clasificación con target comprensible, suficiente histórico y viabilidad de aplicación. Se proporcionaron dos CSV: un histórico de resultados y una fuente detallada de 2025-26.

## Decisión propuesta

Combinar ambas fuentes en una tabla canónica por partido y usar provisionalmente `result_ft` como target multiclase:

- `H`: victoria local.
- `D`: empate.
- `A`: victoria visitante.

La predicción se define antes del inicio del encuentro. La clave de solapamiento es fecha + equipo local + equipo visitante y, si una fila aparece en ambas fuentes, se conserva la detallada.

## Evidencia

- 11.944 partidos, 54 variables y 31 temporadas.
- 0 IDs duplicados, 0 targets ausentes y 0 incoherencias entre goles y resultado.
- Distribución: H 47,2 %, D 25,6 % y A 27,2 %.
- 380 partidos incluyen el bloque detallado 2025-26.
- Informe: `reports/laliga_eda.md`.
- Manifest y huellas: `reports/metrics/dataset_manifest.json`.

## Consecuencias

- Marcadores, tiros, tarjetas, faltas, córners y derivadas del partido actual son leakage crítico y se excluyen del modelado prepartido.
- Las cuotas de apertura pueden ser features si la aplicación garantiza su disponibilidad. Las cuotas de cierre quedan condicionadas a la ventana de inferencia.
- Se recomienda un split temporal y features históricas calculadas únicamente con partidos anteriores.
- Los dos CSV raw se versionan en Git para facilitar la reproducción y revisión del EDA por parte del equipo, y no se alteran. La procedencia y la licencia definitivas siguen pendientes de validación.

## Pendientes antes de aprobar

- Confirmar URL de origen, autoría y licencia de cada CSV.
- Validar problema, usuario y target con los cuatro integrantes.
- Comparar formalmente con otros datasets candidatos o justificar que no aplica.
- Aprobar métrica, splits, semilla, overfitting y modelos candidatos.

Hasta resolver estos puntos no se cierra `Data Ready` ni se inicia entrenamiento.
