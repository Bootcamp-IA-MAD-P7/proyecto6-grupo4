# Predictor de resultados de LaLiga

Este proyecto es una aplicación de inteligencia artificial que **predice el resultado de un partido de fútbol de LaLiga española antes de que se juegue**: si va a ganar el equipo local, si va a haber empate, o si va a ganar el equipo visitante. La predicción se basa únicamente en el historial de partidos anteriores (forma reciente, goles, puntos, fuerza relativa entre equipos, etc.) — **no usa cuotas de apuestas ni datos del partido en curso**, porque el objetivo es predecir *antes* de que el partido empiece.

Es un proyecto académico hecho por un equipo de 4 personas, siguiendo un proceso completo de ciencia de datos: desde conseguir y limpiar los datos, hasta entrenar varios modelos de machine learning, elegir el mejor, y ponerlo a disposición de cualquier persona a través de una página web sencilla.

---

## Índice

1. [¿Cómo ver y hacer una predicción?](#cómo-ver-y-hacer-una-predicción)
2. [¿Dónde se ven los resultados y análisis del proyecto?](#dónde-se-ven-los-resultados-y-análisis-del-proyecto)
3. [¿Cómo se construyó el dataset (los datos)?](#cómo-se-construyó-el-dataset-los-datos)
4. [¿Qué modelos se entrenaron y cuál se eligió?](#qué-modelos-se-entrenaron-y-cuál-se-eligió)
5. [¿Cómo se guardan y consultan los datos (bases de datos)?](#cómo-se-guardan-y-consultan-los-datos-bases-de-datos)
6. [Cómo poner en marcha el proyecto](#cómo-poner-en-marcha-el-proyecto)
7. [Estructura del repositorio](#estructura-del-repositorio)
8. [Pruebas automáticas (tests)](#pruebas-automáticas-tests)
9. [Documentación adicional](#documentación-adicional)

---

## ¿Cómo ver y hacer una predicción?

La forma más simple es a través de la **página web** (el frontend):

1. Se abre la página en el navegador (ver [Cómo poner en marcha el proyecto](#cómo-poner-en-marcha-el-proyecto) más abajo para las instrucciones exactas).
2. Se elige el **equipo local** en el primer menú desplegable.
3. Se elige el **equipo visitante** en el segundo menú desplegable (tiene que ser distinto al local).
4. Se elige la **fecha del partido**.
5. Se pulsa el botón **"Predecir resultado"**.

La página muestra:

- El resultado más probable (**Victoria local**, **Empate** o **Victoria visitante**) con un porcentaje de confianza.
- El desglose de probabilidad de cada uno de los tres resultados posibles.
- Un historial de las predicciones que se han hecho en esa sesión, para poder comparar varias.

Cada predicción también queda registrada internamente (ver el punto 5, sobre bases de datos), y la propia aplicación permite enviar **feedback**: es decir, indicar cuál fue el resultado real del partido una vez jugado, para que quede guardado y se pueda comparar con lo que predijo el modelo.

### Para quien prefiera hacerlo de forma técnica (API)

La predicción también se puede pedir directamente al servidor que hace los cálculos (el "backend"), sin pasar por la página web, con una petición HTTP:

```
POST /api/v1/predictions
{
  "home_team": "Real Madrid",
  "away_team": "Barcelona",
  "match_date": "2026-10-25"
}
```

La respuesta incluye el resultado predicho, las tres probabilidades, qué versión del modelo respondió, y cuánto tardó en calcularse.

---

## ¿Dónde se ven los resultados y análisis del proyecto?

Todo el trabajo de análisis y experimentación queda documentado dentro de la carpeta `reports/`, en documentos legibles (no hace falta saber programar para entenderlos):

| Qué quiero ver | Dónde está |
|---|---|
| Resumen técnico de todo el proyecto: datos, modelos, resultado final | [`reports/technical_report.md`](reports/technical_report.md) |
| Análisis exploratorio de los datos (gráficas, estadísticas) | [`reports/laliga_eda.md`](reports/laliga_eda.md) y las imágenes en `reports/figures/` |
| Comparación numérica de los 4 modelos entrenados | [`reports/experiments/experiments_table.csv`](reports/experiments/experiments_table.csv) |
| Por qué se eligió el modelo final (el "Champion") y sus métricas | [`reports/experiments/champion_metadata.json`](reports/experiments/champion_metadata.json) |
| Cómo se combinaron los 4 modelos en el modelo final | [`reports/experiments/ensemble_abcd_review.md`](reports/experiments/ensemble_abcd_review.md) |
| Validación cruzada (pruebas de estabilidad de cada modelo) | [`reports/experiments/cross_validation_review.md`](reports/experiments/cross_validation_review.md) |

---

## ¿Cómo se construyó el dataset (los datos)?

1. **Origen de los datos.** Se combinaron dos fuentes públicas:
   - Un histórico de partidos de LaLiga desde la temporada 1995-96 (publicado en Kaggle).
   - Estadísticas detalladas de la temporada 2025-26 (publicadas en football-data.co.uk).

   Estas fuentes se usan solo para trabajar dentro de este proyecto: no está autorizado publicarlas ni redistribuirlas fuera de él, porque ninguna de las dos declara una licencia abierta que lo permita explícitamente. El detalle completo de esta verificación está en [`docs/decisions/0001-laliga-dataset-target-proposal.md`](docs/decisions/0001-laliga-dataset-target-proposal.md).

2. **Limpieza y combinación.** Las dos fuentes se combinaron en un único archivo (un partido = una fila), eliminando duplicados, corrigiendo fechas y descartando filas con datos imposibles (por ejemplo, un resultado que no coincide con el marcador, o un equipo jugando contra sí mismo). El resultado final: **11.944 partidos**, desde la temporada 1995-96 hasta la 2025-26.

3. **División temporal (muy importante).** Los partidos se dividieron en tres bloques **por fecha**, nunca al azar, para que el modelo nunca "vea" partidos futuros durante el entrenamiento:
   - **Entrenamiento** (train): temporadas 1995-96 a 2019-20 — 9.607 partidos.
   - **Validación**: temporadas 2020-21 a 2022-23 — 1.197 partidos. Se usa para comparar modelos y elegir el mejor.
   - **Prueba final** (test, "protegida"): temporadas 2023-24 a 2025-26 — 1.140 partidos. Se usa **una sola vez**, al final, para confirmar el resultado del modelo ya elegido — nunca para decidir cuál modelo es mejor.

4. **Variables que usa el modelo (features).** El modelo no conoce el resultado del partido que va a predecir — solo conoce lo que pasó *antes* de ese partido: forma reciente de cada equipo (últimos 5 partidos), goles a favor y en contra, puntos conseguidos, porcentaje de victorias, una puntuación de fuerza tipo "Elo" (similar a la que se usa en ajedrez), y los días de descanso desde el último partido. Nunca se usan cuotas de apuestas, alineaciones, lesiones ni el marcador del propio partido a predecir (eso sería "hacer trampa": usar información que no existe todavía en el momento de predecir).

Los scripts que reproducen todo este proceso son `scripts/run_laliga_preprocessing.py` (limpieza y combinación) y `scripts/run_historical_features.py` (cálculo de las variables anteriores).

---

## ¿Qué modelos se entrenaron y cuál se eligió?

El equipo entrenó **cuatro modelos distintos** (uno por integrante), todos con las mismas reglas y los mismos datos, para poder compararlos de forma justa:

| Modelo | Técnica | Responsable |
|---|---|---|
| A | Regresión logística (un modelo lineal, sencillo e interpretable) | I1 |
| B | Gradient Boosting (árboles de decisión combinados) | I2 |
| C | Random Forest (muchos árboles de decisión combinados) | I3 |
| D | Máquina de vectores de soporte (SVM) con calibración de probabilidades | I4 |

Cada modelo se evaluó con una métrica llamada **macro-F1**, que mide qué tan bien acierta el modelo en las tres categorías (victoria local, empate, victoria visitante) sin favorecer a la más común. También se vigiló el **sobreajuste** (que el modelo memorice el pasado en vez de aprender un patrón real) — dos de los cuatro modelos (B y C) tuvieron sobreajuste alto en su primera versión y se corrigieron antes de continuar.

### El modelo final elegido: un "comité" de los cuatro

Después de corregir y afinar los cuatro modelos, se probó combinarlos en un solo modelo — una especie de "comité" donde los cuatro modelos votan y se promedia su opinión (esto se llama **ensemble por votación suave**). Ese comité resultó ser **mejor que cualquiera de los cuatro modelos por separado**, así que es el que quedó seleccionado como modelo oficial (el "Champion") que responde las predicciones de la aplicación.

**Resultado final, medido sobre partidos que el modelo nunca había visto (los 1.140 de la prueba protegida):**

- Acierta el resultado correcto en aproximadamente **1 de cada 2 partidos** (50,6% de acierto global).
- La métrica principal del proyecto (macro-F1) es **0,48** — en una escala donde 1,0 sería predicción perfecta y 0,33 sería "adivinar al azar" entre las tres opciones.

Esto sitúa al modelo claramente por encima del azar, aunque, como cualquier predicción deportiva, está lejos de ser infalible — el fútbol tiene un componente de imprevisibilidad que ningún modelo estadístico elimina del todo.

---

## ¿Cómo se guardan y consultan los datos (bases de datos)?

Cada vez que alguien pide una predicción o envía feedback a través de la aplicación, esa información se guarda de dos formas complementarias:

### 1. Base de datos PostgreSQL (la forma principal)

Hay dos tablas:

- **`predictions`**: guarda cada predicción hecha (equipos, fecha, resultado predicho, las tres probabilidades, qué versión del modelo respondió, y cuánto tardó).
- **`feedback`**: guarda cada resultado real que alguien reportó después de un partido (para poder comparar, más adelante, lo que predijo el modelo contra lo que pasó de verdad).

El detalle técnico completo de estas tablas (columnas, tipos de dato) está en [`docs/database_schema.md`](docs/database_schema.md).

**Para consultarla** (necesita tener la aplicación corriendo, ver la sección siguiente):

```powershell
docker exec proyecto6-grupo4-postgres-1 psql -U laliga -d laliga -c "SELECT * FROM predictions ORDER BY created_at DESC LIMIT 10;"
docker exec proyecto6-grupo4-postgres-1 psql -U laliga -d laliga -c "SELECT * FROM feedback ORDER BY received_at DESC LIMIT 10;"
```

También se puede usar cualquier programa visual de gestión de bases de datos (por ejemplo DBeaver o pgAdmin), conectándose con estos datos: servidor `localhost`, puerto `5432`, usuario `laliga`, contraseña `laliga`, base de datos `laliga`.

Si la base de datos no está disponible en un momento dado, la aplicación **sigue funcionando igual** para el usuario (sigue respondiendo predicciones); simplemente ese registro puntual no queda guardado en la base de datos.

### 2. Un archivo de respaldo (feedback)

El feedback que se envía queda también guardado, de forma independiente, en un archivo de texto simple (`data/feedback/predictions_feedback.csv`) que se puede abrir con Excel o cualquier editor de texto. Es un respaldo adicional que no depende de tener la base de datos funcionando.

---

## Cómo poner en marcha el proyecto

### Opción recomendada: todo junto con Docker

Esta es la forma más simple: un solo comando levanta la página web, el servidor de predicciones y la base de datos, ya conectados entre sí.

**Requisito previo:** generar una sola vez los archivos del modelo entrenado (esto no hace falta repetirlo salvo que se quiera reentrenar desde cero):

```powershell
.\.venv\Scripts\python.exe scripts\run_laliga_preprocessing.py
.\.venv\Scripts\python.exe scripts\run_historical_features.py
.\.venv\Scripts\python.exe scripts\run_candidate_a.py
.\.venv\Scripts\python.exe scripts\run_candidate_b.py
.\.venv\Scripts\python.exe scripts\run_candidate_c.py
.\.venv\Scripts\python.exe scripts\run_candidate_d.py
.\.venv\Scripts\python.exe scripts\run_ensemble_abcd.py
.\.venv\Scripts\python.exe scripts\select_champion.py
```

**Levantar todo:**

```powershell
docker compose up --build
```

- Página web y servidor de predicciones (mismo servicio, igual que en producción): [http://localhost:8000](http://localhost:8000) (comprobar que funciona con [http://localhost:8000/health](http://localhost:8000/health))
- Base de datos: `localhost:5432`

**Para apagarlo todo:** `docker compose down` (los datos guardados en la base de datos se conservan para la próxima vez).

Instrucciones más detalladas de Docker en [`docker/README.md`](docker/README.md).

### Opción manual (sin Docker)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-eda.txt
.\.venv\Scripts\python.exe -m pip install -r requirements-backend.txt
```

Después de generar los archivos del modelo (mismos comandos que arriba), en una terminal:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.backend.main:app --host 127.0.0.1 --port 8000
```

Y en otra terminal, para servir la página web:

```powershell
.\.venv\Scripts\python.exe -m http.server 5173 --directory app\frontend\public --bind 127.0.0.1
```

Después se abre [http://localhost:5173](http://localhost:5173) en el navegador. Sin Docker no hay base de datos PostgreSQL disponible salvo que se instale y configure aparte (ver `docs/database_schema.md`); la aplicación sigue funcionando igual, solo que sin guardar el historial en base de datos.

---

## Estructura del repositorio

- `app/`: la aplicación — `frontend/` (la página web) y `backend/` (el servidor que calcula las predicciones).
- `data/`: los datos — originales (`raw/`), procesados (`processed/`) y el feedback recibido (`feedback/`).
- `src/data/`: preparación y limpieza de los datos, generación de variables.
- `src/candidates/`: los cuatro modelos (A-D) y el modelo combinado (ensemble).
- `src/evaluation/`: comparación entre modelos, elección del Champion, validación cruzada.
- `src/inference/`: lógica que usa el modelo elegido para responder predicciones reales.
- `src/persistence/`: conexión y guardado en la base de datos.
- `src/feedback/`: guardado del feedback en el archivo de respaldo.
- `models/`: los archivos entrenados de cada modelo y del modelo final (no se suben a este repositorio; se generan localmente con los scripts).
- `reports/`: todos los informes, gráficas y métricas explicados arriba.
- `docker/`: los archivos para levantar todo con Docker.
- `tests/`: las pruebas automáticas que verifican que todo sigue funcionando correctamente.
- `docs/`: documentación adicional y decisiones tomadas por el equipo.
- `.specify/`: el proceso de trabajo del equipo (backlog de tareas, especificación técnica) — es la fuente de referencia interna del proyecto.

---

## Pruebas automáticas (tests)

El proyecto tiene una batería de pruebas automáticas que comprueban que cada parte sigue funcionando correctamente (desde la limpieza de datos hasta las respuestas de la página web). Para ejecutarlas:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Si todo está en orden, el resultado final indica cuántas pruebas pasaron (por ejemplo, `76 passed`).

---

## Documentación adicional

- [`docs/data_acquisition.md`](docs/data_acquisition.md): cómo obtener los archivos de datos originales.
- [`docs/database_schema.md`](docs/database_schema.md): detalle técnico de la base de datos.
- [`docs/decisions/`](docs/decisions/): decisiones importantes que tomó el equipo, con su justificación (qué datos usar, qué modelos entrenar, cómo evaluar, etc.).
- [`.specify/`](.specify/): backlog completo de tareas del proyecto, con el estado y la evidencia de cada una.

### Regla de trabajo para quien contribuya al código

Antes de proponer o modificar código es obligatorio leer completamente:

1. `.specify/0_constitution.md`
2. `.specify/1_intent.md`
3. `.specify/2_spec.md`
4. `.specify/3_plan.md`
5. `.specify/4_tasks.md`

La carpeta `.specify/` es la fuente central de verdad de las reglas y el estado del proyecto.
