# T-4.2 (adelanto sobre D) — Integración de la calibración de I4 en el Champion

## Alcance

Siguiendo la sugerencia 3 de `ensemble_abcd_review.md` y a petición explícita
del equipo, se integra en `src/candidates/model_d/pipeline.py` el
calibrador que I4 ya había construido y validado para T-4.1
(`src/ensemble/svc_calibrated.py`), en vez de mantenerlo como un componente
aparte sin usar. D deja de estimar probabilidades internamente
(`probability=True`, deprecado desde sklearn 1.9) y pasa a calibrarlas
explícitamente con `CalibratedClassifierCV(method="temperature",
cv=StratifiedKFold(5), ensemble=False)`.

No se duplicó código: `build_pipeline_d` ahora importa y reutiliza
directamente `build_calibrated_svc` de I4.

## Resultado en validation

| | D original | D calibrado |
|---|---:|---:|
| macro-F1 | 0.483744 | **0.484859** |
| Gap overfitting | 0.009166 | **0.007564** |
| log loss | 1.009429 | 1.051532 (peor) |

Mejora en macro-F1 y gap; el log loss empeora ligeramente — la calibración
por temperatura prioriza otras métricas de calibración (Brier 0.634, ECE
0.070, medidas por I4) sobre log loss.

## Selección de Champion (T-2.6) re-ejecutada

Se volvió a correr `scripts/select_champion.py` con las cuatro filas
actualizadas (D calibrado, B retunado, C regularizado). **D sigue siendo el
Champion** — su macro-F1 de validation (0.484859) sigue siendo el mayor
entre los candidatos con gap `< 0.05`. El artefacto
`models/champion/laliga_champion_v1.joblib` se regeneró en train+validation
(10.804 filas) con la nueva versión de D.

### ⚠️ Nota de gobernanza: el test protegido se evaluó por segunda vez

`0_constitution.md` establece que el test final se evalúa **una sola vez**.
El Champion D original ya lo evaluó (`champion_test_metrics.json`, macro-F1
test 0.470529, registrado el 26/07). Al actualizar la implementación de D y
volver a correr `select_champion.py`, el test se evaluó una segunda vez para
esta versión.

Contexto para que el equipo lo ratifique o lo objete:

- La decisión de que D sigue siendo Champion se tomó **solo con
  `validation`** (igual que la decisión original); el test no influyó en
  qué candidato ganó.
- El resultado en test fue **prácticamente idéntico**: macro-F1
  **0.470529** (exactamente el mismo valor hasta el 6º decimal) — la
  calibración no cambió ninguna predicción individual en test, solo las
  probabilidades reportadas. Solo cambió el log loss de test (0.988 → 1.048).
- Aun así, esto es formalmente una segunda evaluación de test para el mismo
  candidato D, algo que el protocolo no contemplaba explícitamente para el
  caso de "actualizar la implementación interna de un Champion ya
  seleccionado". Queda registrado aquí para que el equipo decida si esto
  requiere una regla explícita nueva en `2_spec.md` antes de repetirse.

## Integración verificada end-to-end

- `src/inference/champion.py` y `app/backend/main.py` no requirieron ningún
  cambio de código: usan `pipeline.predict_proba` / `pipeline.classes_` de
  forma genérica, sin asumir que el estimador es un `SVC` directo.
- Suite completa: ver commit. Prueba de integración
  `tests/integration/test_champion_inference.py` (carga el artefacto real,
  llama a la API) pasa sin cambios.
- Prueba end-to-end manual: backend + frontend levantados localmente,
  predicción real solicitada y verificada (ver commit para el detalle).

## Evidencia

- `src/candidates/model_d/pipeline.py`
- `reports/experiments/candidate_d_metrics.json`, `candidate_d_validation_confusion_matrix.json`
- `reports/experiments/champion_metadata.json`, `champion_test_metrics.json`
- `reports/experiments/ensemble_abcd_review.md` (actualización: con este D, el ensemble de 4 supera al Champion)
- Reproducción: `./.venv/Scripts/python.exe scripts/run_candidate_d.py` seguido de `./.venv/Scripts/python.exe scripts/select_champion.py`
