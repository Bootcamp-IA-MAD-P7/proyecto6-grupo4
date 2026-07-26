# Revisión de Pipeline D (I4) — 2026-07-26

## Alcance revisado

- Ruta esperada: `src/candidates/model_d/`.
- Rama remota de referencia: `origin/feature/i4-backend-mock`.
- Contrato exigido: features comunes, splits congelados, SVM RBF con
  probabilidades, serialización, métricas y registro experimental.

## Resultado

**No hay entregable de Pipeline D revisable.** La ruta contiene únicamente
`.gitkeep`; la rama de referencia coincide con `develop` en este checkout y no
aporta código, pruebas, artefacto, métricas ni fila experimental de D.

Por tanto no se concede aprobación para T-2.4. Cuando I4 aporte el pipeline,
la revisión debe comprobar al menos que no usa `split=test`, que solo consume
`MODEL_FEATURES`, que el escalado se ajusta en train, que `SVC(kernel="rbf",
probability=True)` y su serialización son reproducibles y que el registro usa
el mismo SHA de datos, manifest de splits y versión de features que los demás
candidatos.
