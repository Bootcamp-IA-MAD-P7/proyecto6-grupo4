# EDA completo — Partidos de LaLiga

## Estado del análisis

Este informe cubre el preprocesamiento T-1.4 y el EDA T-1.3 del dataset canónico provisional de LaLiga. El target propuesto es `result_ft`: **H** (victoria local), **D** (empate) y **A** (victoria visitante). El flujo es reproducible, pero **no cierra `Data Ready`**: la licencia, el protocolo de evaluación y la aprobación cruzada siguen pendientes.

## Resumen ejecutivo

- Se analizaron **11,944 partidos**, **54 variables** y **31 temporadas**, entre 1995-09-02 y 2026-05-24.
- La unión prioriza la fuente detallada en **100 partidos solapados** y termina con **0 IDs duplicados**, **0 targets ausentes** y **0 incoherencias.
- El target está moderadamente desbalanceado: H=5,641 (47.2%), D=3,058 (25.6%) y A=3,245 (27.2%). La baseline mayoritaria es 47.2%.
- La media es **2.67 goles/partido**; 49.5% supera 2,5 goles y 51.7% registra goles de ambos equipos.
- Solo **380 partidos** (3.2%) contienen tiros, faltas, tarjetas y cuotas. Esta ausencia es estructural por temporada y no debe imputarse sobre el histórico.
- En las filas con cuotas completas, escoger el favorito de apertura acierta 54.5%; es una referencia descriptiva, no un modelo entrenado.

![Distribución del target](figures/01_target_distribution.png)

## 1. Fuentes y trazabilidad

Los CSV originales se conservan sin modificación en `data/raw/` y sus SHA-256 están en `reports/metrics/dataset_manifest.json`.

| Archivo raw | Fuente identificada | URL | Obtención | Licencia/uso |
|---|---|---|---|---|
| `LaLiga_Matches.csv` | La Liga Complete Dataset | https://www.kaggle.com/datasets/kishan305/la-liga-results-19952020 | Descarga manual del CSV consolidado publicado en Kaggle. | Data files © Original Authors (según la ficha de Kaggle). |
| `laliga_2025_2026_stats.csv` | Football-Data Spain La Liga 2025/2026 (SP1.csv) | https://www.football-data.co.uk/data.php | Descarga del CSV SP1 de la temporada 2025/2026 y renombrado local. La copia raw corresponde a una instantánea anterior a la versión actualmente publicada. | Football-Data permite acceso gratuito y declara uso para predicción de partidos; no se ha verificado una licencia abierta explícita. |

La procedencia está documentada; la aprobación de uso/licencia sigue abierta. El CSV detallado local es una instantánea anterior a la versión actualmente servida por Football-Data: coincide en temporada, 380 filas y 131 columnas, pero no byte a byte porque las cuotas se actualizan.

## 2. Pipeline de combinación y política de columnas

- Histórico: **11,664 filas y 10 columnas**. Se conservan fecha, equipos, goles y resultados; `Season` solo valida y luego se deriva desde la fecha.
- Detallado: **380 filas y 131 columnas**. Se conservan **39** y se eliminan **92** cuotas específicas/máximas redundantes y con cobertura irregular.
- La política completa, columna por columna, está en `reports/metrics/source_column_policy.csv`.
- Clave de solapamiento: **fecha normalizada + equipo local recortado + equipo visitante recortado**.
- Estrategia: unión vertical, descartando del histórico la clave repetida y conservando la fila detallada. Se usa porque ambas fuentes describen partidos, no entidades diferentes, y la fila detallada contiene el bloque mínimo más estadísticas y promedios de mercado.

## 3. Limpieza y calidad final

Reglas deterministas:

1. Recortar texto y normalizar resultados a H/D/A.
2. Convertir fechas y goles; retirar filas con clave, marcador o target crítico inválido.
3. Eliminar duplicados exactos y duplicados de clave dentro de cada fuente.
4. Resolver los 100 solapamientos priorizando la fila detallada.
5. Conservar los dos nulos de descanso porque son opcionales, posteriores al evento y no se usarán como feature prepartido.
6. No imputar el bloque detallado ausente del histórico: el nulo es estructural.

| Control de limpieza | Histórico | Detallado |
|---|---:|---:|
| Duplicados exactos eliminados | 0 | 0 |
| Filas críticas inválidas eliminadas | 0 | 0 |
| Claves duplicadas internas eliminadas | 0 | 0 |
| Filas tras limpieza de fuente | 11,664 | 380 |

| Control | Resultado |
|---|---:|
| Filas finales | 11,944 |
| Columnas finales | 54 |
| Filas duplicadas completas | 0 |
| IDs de partido duplicados | 0 |
| Target ausente | 0 |
| Filas con descanso incompleto | 2 |
| Resultados incoherentes con goles | 0 |
| Equipos local y visitante iguales | 0 |
| Goles negativos | 0 |

Salida reproducible: `data/processed/laliga_matches_clean.csv`; SHA-256 `6288a872df07a196a48ea05039671feba0616489927ebc12b344d96f0e921b0c`.

![Perfil de valores ausentes](figures/06_missingness_profile.png)

## 4. Distribución y balance del target

La clase H domina, seguida de A y D. El ratio entre clase mayoritaria y minoritaria es **1.84**: existe desbalance moderado, no extremo. Accuracy por sí sola no será suficiente; el protocolo de evaluación debería considerar balanced accuracy y macro-F1, sujeto a T-0.4.

La mezcla de resultados cambia por temporada. La asociación temporada-target es baja (V de Cramér=0.025), pero el orden temporal sigue siendo crítico para evitar evaluar con información futura.

![Target por temporada](figures/02_target_by_season.png)

## 5. Distribuciones, evolución temporal y outliers

Los goles son variables discretas con cola derecha. Los valores extremos identificados por IQR representan goleadas reales plausibles y no errores automáticos; deben validarse, no truncarse por defecto.

La tasa de victoria local y la diferencia media de goles fluctúan a lo largo de las temporadas. Esto indica posible cambio temporal de distribución y recomienda particiones cronológicas y features de forma calculadas únicamente con partidos anteriores.

![Distribución de goles](figures/03_goals_distribution.png)

![Ventaja local](figures/04_home_advantage_trend.png)

| Variable | Límite inferior IQR | Límite superior IQR | Outliers | Porcentaje |
|---|---:|---:|---:|---:|
| `red_cards_away` | 0.0 | 0.0 | 49 | 12.9% |
| `red_cards_home` | 0.0 | 0.0 | 42 | 11.1% |
| `home_goals_ft` | -0.5 | 3.5 | 973 | 8.1% |
| `shots_away` | -1.0 | 23.0 | 12 | 3.2% |
| `shots_on_target_away` | -2.5 | 9.5 | 9 | 2.4% |
| `yellow_cards_away` | -2.0 | 6.0 | 8 | 2.1% |
| `shots_home` | -0.5 | 27.5 | 3 | 0.8% |
| `fouls_home` | 2.5 | 22.5 | 3 | 0.8% |
| `yellow_cards_home` | -2.0 | 6.0 | 1 | 0.3% |
| `away_goals_ft` | -3.0 | 5.0 | 31 | 0.3% |
| `total_goals` | -3.5 | 8.5 | 21 | 0.2% |
| `shots_on_target_home` | -3.0 | 13.0 | 0 | 0.0% |
| `fouls_away` | 1.0 | 25.0 | 0 | 0.0% |

![Perfil de outliers](figures/11_outlier_profile.png)

Conclusión: los extremos de goles, tiros y tarjetas son observaciones deportivas plausibles. No se eliminan automáticamente; la limpieza retira errores lógicos, no partidos raros pero válidos.

## 6. Equipos y cardinalidad

Hay 48 equipos distintos en el rol local. `match_id` es único al 100.0% y debe tratarse exclusivamente como identificador. Los nombres de equipo sí pueden aportar señal, pero requieren una estrategia capaz de manejar ascensos, descensos y categorías no vistas. Una alternativa más robusta es derivar forma, Elo o promedios móviles usando solo el pasado.

La asociación bruta del equipo local con el target es V=0.171 y la del visitante V=0.183; no implican causalidad.

![Rendimiento histórico de equipos](figures/05_team_performance.png)

## 7. Relaciones entre variables y target

En 2025-26, tiros y tiros a puerta se relacionan con goles y resultado, como cabe esperar. Esa relación es **descriptiva y posterior al evento**: usarla para predecir el mismo partido produciría leakage crítico.

Las cuotas de apertura sí existen antes del partido y muestran señal predictiva. Su uso es viable si la aplicación garantiza la misma fuente y momento de captura. Las cuotas de cierre tienen riesgo temporal porque pueden no estar disponibles cuando se solicita la predicción.

![Correlaciones detalladas](figures/07_detailed_correlation_heatmap.png)

![Relaciones con el target](figures/08_relationships_with_target.png)

## 8. Matrices de confusión descriptivas

No se entrena ningún candidato porque `.specify` mantiene bloqueados splits y modelos. Se incluyen dos reglas de referencia:

1. **Clase mayoritaria** sobre todo el dataset: siempre predice H y alcanza 47.2%. Evidencia que accuracy puede ocultar un fallo total en D y A.

| Real \ Predicha | H | D | A |
|---|---:|---:|---:|
| H | 5641 | 0 | 0 |
| D | 3058 | 0 | 0 |
| A | 3245 | 0 | 0 |

![Baseline mayoritaria](figures/10_majority_baseline_confusion.png)

2. **Favorito de cuotas de apertura** sobre 380 partidos 2025-26: elige la mayor probabilidad implícita y acierta 54.5%. No es un modelo entrenado ni una evaluación final.

| Real \ Favorito | H | D | A |
|---|---:|---:|---:|
| H | 160 | 0 | 26 |
| D | 62 | 0 | 31 |
| A | 54 | 0 | 47 |

![Baseline de mercado](figures/09_market_baseline_confusion.png)

## 9. Riesgo de leakage

Se deben excluir del entrenamiento prepartido del mismo encuentro:

- Marcador final y al descanso, resultado al descanso y todas sus derivadas.
- Tiros, tiros a puerta, faltas, córners y tarjetas.
- `total_goals`, diferencias, clean sheets, puntos, over 2,5 y ambos marcan.
- Metadatos de fuente/cobertura, que revelan la temporada y el mecanismo de captura.
- `match_id`, que no tiene valor predictivo generalizable.

La fecha, temporada y equipos son inputs disponibles, pero no deben transformarse usando datos futuros. Las cuotas de cierre quedan condicionadas a definir la ventana de inferencia.

## 10. Viabilidad para una aplicación

Inputs directamente solicitables: equipo local, visitante, fecha/hora y, si existe una integración externa aprobada, cuotas prepartido. Para ofrecer valor sin depender de casas de apuestas, el pipeline debería generar forma reciente, fuerza ofensiva/defensiva y rating histórico a partir de partidos anteriores.

No son inputs aceptables: goles, tiros, tarjetas o cualquier estadística ocurrida durante/después del partido que se intenta predecir.

## 11. Reglas comunes propuestas

1. Mantener ambos CSV raw inmutables y verificar sus SHA-256.
2. Deduplicar por fecha + local + visitante y priorizar la fila detallada.
3. Normalizar fechas, temporada y tipos con el loader común.
4. No imputar el bloque detallado sobre 1995-96–2024-25: es ausencia estructural.
5. Excluir leakage y metadatos antes de modelar.
6. Construir features históricas con `shift`/ventanas cerradas al pasado.
7. Usar un split temporal; no congelarlo hasta aprobar T-0.4.
8. Proteger el test final y ajustar transformaciones solo con train.

## 12. Limitaciones y decisiones pendientes

- Las URL y la trazabilidad ya están documentadas; falta que el equipo apruebe las condiciones de uso/licencia.
- El target, el usuario y la ventana de predicción son propuestas que requieren aprobación del equipo.
- El bloque detallado representa una única temporada y no permite asumir estabilidad histórica.
- Las primeras temporadas contienen más partidos por cambios de tamaño de la liga; comparar conteos brutos sin normalizar puede inducir a error.
- Las matrices mostradas son reglas descriptivas; no se han creado splits ni entrenado candidatos.

## Reproducibilidad

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-eda.txt
.\.venv\Scripts\python.exe scripts\run_laliga_preprocessing.py
.\.venv\Scripts\python.exe scripts\run_laliga_eda.py
.\.venv\Scripts\python.exe scripts\create_preprocessing_notebook.py
.\.venv\Scripts\python.exe scripts\create_eda_notebook.py
.\.venv\Scripts\python.exe scripts\execute_eda_notebook.py
.\.venv\Scripts\python.exe -m pytest
```

Los artefactos métricos se guardan en `reports/metrics/`, las figuras en `reports/figures/` y el dataset limpio versionable en `data/processed/laliga_matches_clean.csv`.
