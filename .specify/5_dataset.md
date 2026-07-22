# SPEC 5 — Dataset canónico: alfabeto dactilológico LSE

## Estado de la decisión

- **Dataset seleccionado:** Spanish Sign Language (LSE) Fingerspelling Dataset.
- **Dominio:** Lengua de Signos Española (LSE), alfabeto dactilológico.
- **Problema propuesto:** clasificación multiclase de una configuración manual estática a partir de una imagen.
- **Unidad de predicción:** una imagen de una única mano/configuración estática.
- **Target provisional:** letra LSE asociada a la imagen.
- **Estado del target:** debe validarse contra las carpetas y metadata descargadas antes del gate `Data Ready`.

La aplicación asociada al dataset describe 23 signos estáticos:

`A, B, C, CH, D, E, F, G, H, I, K, L, M, N, O, P, Q, R, S, T, U, W, X`.

Esta lista es una hipótesis documentada para diseñar contratos preliminares, no sustituye la auditoría del dataset. El alcance no incluye letras dinámicas, palabras, secuencias, gramática ni traducción completa de LSE.

## Fuente, acceso y versión

- **Registro oficial:** [Zenodo — Spanish Sign Language (LSE) Fingerspelling Dataset](https://zenodo.org/records/21351703)
- **DOI persistente:** [https://doi.org/10.5281/zenodo.21351703](https://doi.org/10.5281/zenodo.21351703)
- **Repositorio asociado:** [ecabestadistica/LSE-App](https://github.com/ecabestadistica/LSE-App)
- **Fecha del registro consultado:** 16 de julio de 2026.
- **Volumen declarado:** más de 160.000 imágenes.
- **Tamaño total publicado:** 24,9 GB comprimidos.

### Archivos publicados

| Archivo | Resolución | Tamaño | MD5 | Descarga |
|---|---:|---:|---|---|
| `192.zip` | 192×192 | 12,3 GB | `851de347230f9b70686a3c10fc0c0d64` | [Zenodo](https://zenodo.org/records/21351703/files/192.zip?download=1) |
| `512.zip` | 512×512 | 12,6 GB | `4b3f7a89aae41f5003a72a7253a85b91` | [Zenodo](https://zenodo.org/records/21351703/files/512.zip?download=1) |

Cada resolución contiene:

- `Original`: imagen original.
- `Keypoints`: landmarks de la mano sobre fondo negro.
- `Original-Keypoints`: imagen original con landmarks superpuestos.
- Particiones `Train`, `Validation` y `Evaluation`, organizadas por letra según la descripción oficial.

## Licencia y atribución obligatoria

El dataset se publica bajo licencia **Creative Commons Attribution 4.0 International (CC BY 4.0)**. Su reutilización exige atribución adecuada. La licencia del repositorio de código asociado es distinta y no debe confundirse con la licencia del dataset.

La siguiente cita se conservará literalmente en el README, informe técnico, presentaciones y cualquier publicación o entrega que use los datos:

> Marroquín Garcia de Madariaga, I., Cabana Garceran del Vall, E.& LILLO, R. E. (2026). Spanish Sign Language (LSE) Fingerspelling Dataset [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.21351703

No se eliminará ni reformateará esta referencia sin aprobación del equipo.

## Justificación de la elección

### Valor educativo y de producto

- Plantea un problema real de visión por computador con impacto social y un contexto español poco habitual en proyectos formativos.
- La predicción es fácil de explicar: dada una imagen de una configuración manual, el modelo estima una letra del alfabeto dactilológico LSE.
- Permite construir una demostración visual atractiva mediante carga de imagen y, más adelante, captura de cámara.
- Obliga a aprender el ciclo completo de un proyecto de imágenes: estructura de carpetas, transformaciones, extracción de características, clasificación, inferencia y control de latencia.
- Las representaciones `Original`, `Keypoints` y `Original-Keypoints` permiten comparar cuánto aporta el fondo, la forma de la mano y los landmarks.
- El tamaño es suficiente para separar entrenamiento, validación y evaluación y medir overfitting con mayor estabilidad que en datasets pequeños.
- El mismo dominio admite progresión acumulativa: modelos clásicos sobre features/keypoints para el Nivel Esencial y una CNN comparable para el Nivel Experto.

### Comparación que sustenta la decisión

| Candidato | Unidad base | Atractivo de producto | Principal limitación frente a LSE |
|---|---:|---|---|
| **LSE Fingerspelling — seleccionado** | Más de 160.000 imágenes publicadas | Muy alto: predicción visual y contexto español | Descarga pesada, posible leakage entre variantes y alcance limitado a signos estáticos |
| GTZAN | 1.000 canciones | Alto: clasificación de género musical | Pocas canciones independientes; los 9.990 segmentos no son muestras independientes |
| LaLiga 2019–2025 | 2.350 partidos, 4.700 perspectivas de equipo | Alto y cercano al público español | Menor tamaño y riesgo de leakage temporal o variables posteriores al partido |
| Incident Management | 24.918 incidentes, 141.712 eventos | Útil para procesos empresariales | Menos visual y con leakage si se mezclan estados futuros del mismo incidente |

LSE se selecciona porque combina originalidad, utilidad demostrable, volumen y una evolución natural desde clasificación clásica hasta deep learning sin cambiar de dominio.

## Riesgos y controles obligatorios

### Independencia y leakage

Las más de 160.000 imágenes publicadas no deben asumirse automáticamente como 160.000 capturas independientes. Una misma captura puede existir en más de una resolución o representación.

Controles:

1. Construir un identificador de captura base antes de crear o validar splits.
2. Mantener juntas todas las variantes y resoluciones de una captura.
3. Auditar si las mismas personas o sesiones aparecen en varias particiones.
4. No concatenar variantes como si fueran observaciones nuevas.
5. Ajustar augmentations y transformaciones solo con entrenamiento.
6. Reservar `Evaluation` para una única evaluación final si supera la auditoría.

### Coste técnico

- Descargar los dos ZIP supone 24,9 GB y duplica resoluciones del mismo contenido conceptual.
- Entrenar directamente con 512×512 incrementa memoria, tiempo y tamaño del modelo.
- La recomendación inicial para el Nivel Esencial es evaluar `192.zip` y elegir una sola representación canónica; esta elección deberá aprobarse tras inspeccionar calidad y distribución.
- Los ZIP y las imágenes extraídas no se versionarán en Git. Se almacenarán bajo `data/raw/` y se verificará su MD5.

### Alcance y uso responsable

- El prototipo clasifica letras estáticas; no interpreta conversaciones ni sustituye a profesionales de traducción o interpretación de LSE.
- Deben documentarse fallos por iluminación, encuadre, orientación, tono de piel, lateralidad y diferencias entre personas.
- Las imágenes de manos pueden contener información biométrica o contextual. No se recopilarán ni persistirán imágenes nuevas sin necesidad, consentimiento y una política aprobada.
- Una precisión global alta no bastará: se revisarán métricas por clase, matriz de confusión y errores entre configuraciones visualmente próximas.

## Política de adquisición reproducible

1. Descargar únicamente el archivo de resolución aprobado desde Zenodo.
2. Guardar el ZIP sin modificar en `data/raw/`.
3. Verificar el MD5 publicado antes de extraerlo.
4. Registrar fecha, nombre, tamaño, MD5 y DOI en metadata versionada.
5. Extraer de forma reproducible sin renombrar ni sobrescribir el original.
6. Auditar estructura, clases, número de archivos, duplicados y relación entre variantes.
7. Seleccionar una representación canónica para los cuatro candidatos.
8. No iniciar entrenamiento hasta completar el gate `Data Ready`.

La documentación del acceso deja el dataset disponible para todo el equipo, pero la descarga y el loader común corresponden a `T-1.1`; no se duplicarán por integrante.

## Contrato preliminar de aplicación para I3/I4

Entrada mínima propuesta:

- Un archivo de imagen.
- Formatos y tamaño máximo pendientes de validar con el loader y el modelo.
- Una única mano/configuración visible; los casos sin mano o con varias manos deben producir un error controlado o estado `sin_prediccion`.

Salida mínima propuesta:

- `predicted_class`: letra LSE estimada.
- `confidence`: confianza calibrada o score claramente identificado.
- `model_version`: versión del pipeline servido.
- `status`: predicción válida, baja confianza o error de validación.

Este contrato permite crear mocks, pero solo se convertirá en contrato definitivo después de aprobar preprocesamiento, clases, umbral y arquitectura en `T-0.6`.
