# Verificación del despliegue público — T-5.4

Fecha inicial: 2026-07-28

Última revalidación: 2026-07-30

Responsable: I4

## Entorno

- Plataforma: Render.
- Blueprint: servicio web Docker y PostgreSQL administrado.
- Región: Frankfurt.
- Rama desplegada: `develop`.
- Commit desplegado: `fb3d02108b56b51c5f01915c147a2ff78451def7`.
- URL pública: <https://laliga-predictor-grupo4.onrender.com/>.
- Champion: `ensemble_abcd_soft_voting_v1`.
- Artefacto: release `model-ensemble-abcd-soft-voting-v1-f9c0e933`.
- SHA-256 del artefacto: `f9c0e93317924613e9dc8fb57125ecd5b227fdb0afa6fc7ec1f6e963407d5696`.
- SHA-256 del dataset: `56e59efa9200042f76638beafd47feaf67a41a28c00c02aa521192739a607104`.
- Despliegue: manual, porque `render.yaml` mantiene `autoDeployTrigger: off`.

## Verificación externa final

| Comprobación | Resultado |
|---|---|
| `GET /` | HTTP 200; interfaz LaLiga disponible |
| `GET /health` | `status=ok`, `model_loaded=true` |
| Versión cargada | `ensemble_abcd_soft_voting_v1` |
| Predicción | Real Madrid–Barcelona, fecha 2026-10-25: `A` |
| Probabilidades | H `0,256473`; D `0,331361`; A `0,412167`; suma `1,0` |
| Latencia interna informada | `340,51 ms` |
| Hash de datos | Coincide con `champion_metadata.json`: `56e59efa...` |
| JSON malformado | HTTP `400`; código `MALFORMED_JSON` |
| Cuerpo superior a 4 KiB | HTTP `413`; código `PAYLOAD_TOO_LARGE` |
| Suite automática vigente | `91 passed`, según el informe técnico del commit desplegado |

## Incidencia y corrección

La primera versión desplegada reconstruía las features de los 11.944 partidos
en cada petición y superaba los 36 segundos. La PR #71 incorporó
`HistoricalFeatureSnapshot`: el estado de cada equipo se calcula una sola vez
al cargar el Champion y las predicciones futuras reutilizan ese snapshot.

La equivalencia con el generador histórico completo está cubierta por tests.
En el contenedor Linux la petición bajó a `541 ms` observados y, tras el
redeploy público, a `241 ms`.

## Revalidación posterior a PR #78

El 30/07/2026 se actualizó `develop` mediante fast-forward y se desplegó
manualmente el commit `fb3d021`, que incorpora la configuración de logging
por petición y el resto de correcciones de la fase 4.

La comprobación posterior al estado `Live` confirmó que Render ya no servía
el dataset anterior: tanto el modelo como el hash de datos coinciden con los
metadatos versionados. También se ejercitaron en el servicio público los
errores contractuales de JSON malformado y límite de tamaño. Las solicitudes
generaron identificadores trazables (`request_id`) sin registrar el payload
completo.

## Limitaciones operativas

- El plan gratuito puede apagar el servicio por inactividad; el primer health
  después de un arranque en frío puede tardar más.
- La base PostgreSQL gratuita de Render tiene vigencia limitada.
- Antes de una demostración conviene abrir `/health` y esperar una respuesta
  correcta para asegurar que el Champion ya está cargado.
- Como el despliegue automático está desactivado, toda nueva fusión que deba
  llegar a producción requiere `Manual Deploy` → `Deploy latest commit`.
