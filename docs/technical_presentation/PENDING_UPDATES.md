# Pendiente de actualizar — presentación técnica

Revisión 2026-07-30: `proy6_g4_presentacion_tecnica.pptx` tiene cada
diapositiva exportada como una única imagen rasterizada (no hay texto
editable en el XML), así que no se puede corregir con una edición de texto
directa — requiere rediseñar las diapositivas afectadas y reexportarlas.
Se deja este registro para que el equipo lo priorice, en vez de regenerarlo
de forma unilateral (cambiar quién aparece como "Champion" toca directamente
la atribución individual de Fernanda/I4 en la diapositiva 10).

## Diapositivas que necesitan actualizarse

- **Diapositiva 3** ("La idea"): pie dice `Modelo: SVM (Champion)`. El
  Champion vigente es el ensemble `ENSEMBLE_ABCD` (A+B+C+D), no el SVM
  individual (modelo D).
- **Diapositiva 7** ("Stack del proyecto"):
  - Frontend: dice `React + TypeScript + Vite`. La implementación real es
    HTML + CSS + JavaScript plano, sin build (ver `.specify/2_spec.md`,
    revisado 2026-07-29).
  - Persistencia: dice `Archivos (CSV + joblib) — Sin base de datos`. El
    proyecto sí tiene persistencia en PostgreSQL desde T-5.3
    (`src/persistence/`), con fallback a SQLite en memoria.
- **Diapositiva 10** ("El modelo que quedó en producción"): presenta
  `Modelo D, SVM con kernel RBF` como Champion con macro-F1 0.484 y gap
  0.009. El Champion vigente es el ensemble ABCD, macro-F1 validation
  0.485252, gap 0.005385 (ver `reports/experiments/champion_metadata.json`).
- **Diapositiva 11** ("Arquitectura — de la petición a la predicción"):
  mismos dos problemas que la diapositiva 7: `Frontend React + TS`,
  `Modelo: SVM (Champion)`, y `Persistencia: Archivos (CSV + joblib)` sin
  mencionar PostgreSQL.
- **Diapositiva 14** ("Contenedores & DevOps"): incluye `Nginx` como
  reverse proxy en el flujo de despliegue. Desde el fix de duplicidad de
  Docker (2026-07-30), nginx ya no forma parte de la arquitectura: el
  backend sirve el frontend directamente vía `StaticFiles`, igual que en
  Render. También sigue sin mencionar PostgreSQL en persistencia.

## Diapositivas que SÍ siguen vigentes (no tocar)

Diapositivas 1, 2, 4, 5, 6, 8, 9, 12, 13, 15 — contenido histórico o
metodológico que no depende de qué modelo es el Champion (contexto del
dataset, objetivo, spec-driven development, ejemplo de overfitting de C,
demo de la app, roadmap, cierre).
