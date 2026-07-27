# Revisión de Pipeline D (I4) — 2026-07-26

## Alcance revisado

- Ruta esperada: `src/candidates/model_d/`.
- Rama remota de referencia: `origin/feature/i4-backend-mock`.
- Contrato exigido: features comunes, splits congelados, SVM RBF con
  probabilidades, serialización, métricas y registro experimental.

## Resultado

Entrega revisada y aprobada: `src/candidates/model_d/pipeline.py` consume solo
`MODEL_FEATURES`, filtra train/validation antes de `fit`, escala solo en train,
usa `SVC(kernel="rbf", probability=True)` y serializa el pipeline completo.
La fila D comparte SHA, manifest y versión de features con A–C. Resultado:
macro-F1 validation 0,483744; gap 0,009166. El modelo fue elegido Champion.
