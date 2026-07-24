# Tabla de experimentos (T-2.5)

Plantilla vacía para consolidar los cuatro candidatos bajo el mismo contrato de experimentación. Coordina I2; cada integrante rellena la fila de su candidato al terminar T-2.1–T-2.4. No contiene resultados todavía: `T-1.8` (`Data Ready`) sigue abierto y ningún candidato se ha entrenado.

## Columnas de `experiments_table.csv`

| Columna | Contenido esperado |
|---|---|
| `candidate_id` | `A`, `B`, `C` o `D`. No editable. |
| `member` | Integrante responsable (`I1`–`I4`). No editable. |
| `algorithm` | Algoritmo aprobado en `docs/decisions/0003-four-candidate-models.md` (no cambiar sin actualizar esa ADR). |
| `data_version_sha256` | SHA-256 de `data/processed/laliga_matches_clean.csv` usado para entrenar (debe coincidir con `reports/metrics/split_manifest.json`). |
| `split_manifest_reference` | Ruta o hash del manifest de particiones usado (`reports/metrics/split_manifest.json`). |
| `features_version` | Identificador/hash de la tabla común de features prepartido (pendiente de que exista el generador común). |
| `transformations_summary` | Resumen breve de imputación, codificación, escalado y balanceo aplicados solo sobre train. |
| `hyperparameters` | Hiperparámetros finales del estimador, en formato compacto (ej. JSON de una línea). |
| `seed` | Semilla usada en el candidato (`42` salvo justificación registrada). |
| `train_macro_f1` / `validation_macro_f1` | Métrica principal aprobada en T-0.4. |
| `overfitting_gap_macro_f1` | `train_macro_f1 - validation_macro_f1`, en puntos absolutos; debe ser `< 0.05` para poder optar a Champion. |
| `train_accuracy` / `validation_accuracy` / `validation_balanced_accuracy` | Métricas secundarias. |
| `validation_log_loss` | Calibración de probabilidades en validación. |
| `cv_summary_reference` | Ruta a un JSON con media/desviación por fold, si se aplicó validación cruzada. |
| `confusion_matrix_reference` | Ruta a un JSON/CSV con la matriz de confusión 3x3 en validación. |
| `training_time_seconds` / `inference_time_ms` | Tiempos medidos, no estimados. |
| `artifact_path` | Ruta al pipeline serializado completo (transformaciones + estimador). |
| `evidence_path` | Carpeta o notebook con el registro reproducible del experimento. |
| `limitations_and_errors` | Limitaciones observadas y errores típicos del candidato. |
| `status` | `pending`, `in_progress`, `ready_for_comparison` o `disqualified` (con motivo en `limitations_and_errors`). |

## Reglas al rellenar (heredadas de `2_spec.md` y `0_constitution.md`)

- Ninguna fila puede usar el split `test` de `data/processed/splits/laliga_splits.csv`: esas columnas se calculan solo con `train`/`validation`. El test se evalúa una única vez en T-2.6, tras seleccionar el Champion.
- Los cuatro candidatos deben compartir `data_version_sha256` y `split_manifest_reference`; si no coinciden, la comparación no es válida y debe señalarse en `4_tasks.md` antes de continuar.
- `hyperparameters` y `seed` deben permitir reproducir el resultado exacto a partir del `artifact_path`.
- No editar `candidate_id`, `member` ni `algorithm` sin actualizar `docs/decisions/0003-four-candidate-models.md`.
