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

**Cerrado el 2026-07-26.** I2 revisó T-1.4a; el frontend y backend están
integrados, y el checklist de `2_spec.md` no conserva decisiones bloqueantes.
El manifest fija los datos, splits y el contrato histórico usados por los cuatro
candidatos. El test permaneció reservado hasta la selección de Champion.
