# Verificación del despliegue público — T-5.4

Fecha: 2026-07-28

Responsable: I4

## Entorno

- Plataforma: Render.
- Blueprint: servicio web Docker y PostgreSQL administrado.
- Región: Frankfurt.
- Rama desplegada: `develop`.
- URL pública: <https://laliga-predictor-grupo4.onrender.com/>.
- Champion: `ensemble_abcd_soft_voting_v1`.
- Artefacto: release `model-ensemble-abcd-soft-voting-v1`.
- SHA-256: `6333eb87342f9997d764ba416b3a7a434ab2d20df801fa210c0b08bbb7a1bd77`.

## Verificación externa final

| Comprobación | Resultado |
|---|---|
| `GET /` | HTTP 200; interfaz LaLiga disponible |
| `GET /health` | `status=ok`, `model_loaded=true` |
| Versión cargada | `ensemble_abcd_soft_voting_v1` |
| Predicción | Real Madrid–Barcelona, fecha 2026-10-25: `H` |
| Probabilidades | H `0,372396`; D `0,296248`; A `0,331355`; suma `1,0` |
| Tiempo HTTP observado | `241 ms` |
| Latencia interna informada | `50,49 ms` |
| Suite automática | `80 passed` |

## Incidencia y corrección

La primera versión desplegada reconstruía las features de los 11.944 partidos
en cada petición y superaba los 36 segundos. La PR #71 incorporó
`HistoricalFeatureSnapshot`: el estado de cada equipo se calcula una sola vez
al cargar el Champion y las predicciones futuras reutilizan ese snapshot.

La equivalencia con el generador histórico completo está cubierta por tests.
En el contenedor Linux la petición bajó a `541 ms` observados y, tras el
redeploy público, a `241 ms`.

## Limitaciones operativas

- El plan gratuito puede apagar el servicio por inactividad; el primer health
  después de un arranque en frío puede tardar más.
- La base PostgreSQL gratuita de Render tiene vigencia limitada.
- Antes de una demostración conviene abrir `/health` y esperar una respuesta
  correcta para asegurar que el Champion ya está cargado.
