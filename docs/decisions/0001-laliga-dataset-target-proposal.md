# ADR 0001 — Dataset y target de LaLiga

- Estado: aceptada técnicamente el 22/07/2026. Revisión de condiciones completada por I1 el 23/07/2026: uso local compatible con la finalidad publicada; redistribución pública no demostrada. Los CSV se conservan para ejecución local desde el 24/07/2026; pendiente ratificación del equipo y permiso escrito antes de hacerlos públicos.
- Fecha: 2026-07-22.
- Tareas relacionadas: T-0.2a, T-0.2b, T-0.3, T-1.1, T-1.2 y T-1.3.

## Contexto

El proyecto necesita un único dataset de clasificación con target comprensible, suficiente histórico y viabilidad de aplicación. Se proporcionaron dos CSV: un histórico de resultados y una fuente detallada de 2025-26.

## Decisión

Combinar ambas fuentes en una tabla canónica por partido y usar `result_ft` como target multiclase:

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
- Los dos CSV raw se mantienen inmutables para la ejecución local, pero no deben redistribuirse públicamente sin permiso explícito. La procedencia y la revisión de condiciones se registran en `reports/metrics/source_provenance.json`; la adquisición local se documenta en `docs/data_acquisition.md`.
- El dataset canónico limpio se materializa localmente en `data/processed/laliga_matches_clean.csv`; no sustituye a los raw y puede regenerarse determinísticamente.

## Pendientes antes de cerrar `Data Ready`

- Obtener ratificación de I2, I3 e I4 sobre la decisión de uso local y no redistribución.
- Antes de publicar el repositorio, adjuntar permiso escrito de redistribución para ambas fuentes o mover los CSV raw y derivados fila a fila a almacenamiento privado con acceso controlado.
- Resolver y cerrar GitHub issue #41, que registra T-0.2b como prioridad P0.
- Comparar formalmente con otros datasets candidatos o justificar que no aplica.
- Aprobar métrica, splits, semilla, overfitting y modelos candidatos.

La selección técnica, el usuario, la unidad partido y el target constan aprobados en la daily del 22/07/2026. La revisión I1 concluye que la descarga y el uso para predicción son compatibles con la finalidad publicada, pero que acceso gratuito no equivale a permiso de redistribución. Hasta completar la ratificación y la remediación no se cierra `Data Ready` ni se inicia entrenamiento.
