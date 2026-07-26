# Estado del gate Data Ready — 2026-07-26

## Evidencia técnica nueva

- `historical_features_v1` se regenera con `python scripts/run_historical_features.py`.
- El manifest `historical_features_manifest.json` vincula el dataset canónico
  `6288a872df07a196a48ea05039671feba0616489927ebc12b344d96f0e921b0c`, el
  schema, los parámetros y los conteos congelados 9.607/1.197/1.140.
- Las pruebas cubren orden temporal estable, primer partido, historial anterior,
  partidos de la misma fecha, mutación de un resultado futuro y reproducibilidad
  sobre el dataset local.
- Las variables postpartido, `match_id`, cobertura y `result_ft` actual quedan
  fuera de `MODEL_FEATURES`.

## Dictamen

**No cerrado.** Falta la revisión obligatoria de I2 de T-1.4a y siguen abiertas
T-1.6 (mock de frontend) y T-1.7 (mock de backend). Por las reglas de
`.specify/`, esos elementos impiden habilitar formalmente T-2.1–T-2.4. El
artefacto y las métricas de A son evidencia técnica reproducible, no una
autorización para usar el test ni para seleccionar un Champion.
