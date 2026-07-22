# EDA completo — Partidos de LaLiga

## Estado del análisis

Este EDA cubre el dataset canónico provisional de partidos de LaLiga y responde a T-1.3 de `.specify`. El target propuesto es `result_ft`: **H** (victoria local), **D** (empate) y **A** (victoria visitante). El análisis es reproducible, pero **no cierra el gate `Data Ready`**: la procedencia/licencia de las fuentes y la aprobación cruzada del equipo siguen pendientes.

## Resumen ejecutivo

- Se analizaron **11,944 partidos**, **54 variables** y **31 temporadas**, entre 1995-09-02 y 2026-05-24.
- La integración conserva una fila por partido: **0 IDs duplicados**, **0 targets ausentes** y **0 incoherencias** entre goles y resultado.
- El target está moderadamente desbalanceado: H=5,641 (47.2%), D=3,058 (25.6%) y A=3,245 (27.2%). La baseline mayoritaria es 47.2%.
- La media es **2.67 goles/partido**; 49.5% supera 2,5 goles y 51.7% registra goles de ambos equipos.
- Solo **380 partidos** (3.2%) contienen tiros, faltas, tarjetas y cuotas. Esta ausencia es estructural por temporada y no debe imputarse sobre el histórico.
- En las filas con cuotas completas, escoger el favorito de apertura acierta 54.5%; es una referencia descriptiva, no un modelo entrenado.

![Distribución del target](figures/01_target_distribution.png)

## 1. Alcance, unidad de análisis y target

La unidad es un partido de Primera División. La tabla combina un histórico 1995-96–2025-26 con una fuente detallada completa para 2025-26. Los 100 partidos presentes en ambas fuentes se deduplican mediante fecha + local + visitante y se conserva la fila detallada.

`result_ft` es adecuado como target categórico multiclase y no contiene nulos. Sin embargo, la utilidad de negocio y la ventana exacta de predicción deben aprobarse: este informe asume **predicción prepartido antes del inicio**.

## 2. Calidad de datos

| Control | Resultado |
|---|---:|
| Filas duplicadas completas | 0 |
| IDs de partido duplicados | 0 |
| Target ausente | 0 |
| Filas con descanso incompleto | 2 |
| Resultados incoherentes con goles | 0 |
| Equipos local y visitante iguales | 0 |
| Goles negativos | 0 |

Los dos nulos al descanso deben conservarse como desconocidos. No afectan al target, y eliminar esas filas reduciría datos sin beneficiar un modelo prepartido porque las variables de descanso están excluidas por leakage.

![Perfil de valores ausentes](figures/06_missingness_profile.png)

## 3. Distribución y balance del target

La clase H domina, seguida de A y D. El ratio entre clase mayoritaria y minoritaria es **1.84**: existe desbalance moderado, no extremo. Accuracy por sí sola no será suficiente; el protocolo de evaluación debería considerar balanced accuracy y macro-F1, sujeto a T-0.4.

La mezcla de resultados cambia por temporada. La asociación temporada-target es baja (V de Cramér=0.025), pero el orden temporal sigue siendo crítico para evitar evaluar con información futura.

![Target por temporada](figures/02_target_by_season.png)

## 4. Distribuciones, extremos y evolución temporal

Los goles son variables discretas con cola derecha. Los valores extremos identificados por IQR representan goleadas reales plausibles y no errores automáticos; deben validarse, no truncarse por defecto.

La tasa de victoria local y la diferencia media de goles fluctúan a lo largo de las temporadas. Esto indica posible cambio temporal de distribución y recomienda particiones cronológicas y features de forma calculadas únicamente con partidos anteriores.

![Distribución de goles](figures/03_goals_distribution.png)

![Ventaja local](figures/04_home_advantage_trend.png)

## 5. Equipos y cardinalidad

Hay 48 equipos distintos en el rol local. `match_id` es único al 100.0% y debe tratarse exclusivamente como identificador. Los nombres de equipo sí pueden aportar señal, pero requieren una estrategia capaz de manejar ascensos, descensos y categorías no vistas. Una alternativa más robusta es derivar forma, Elo o promedios móviles usando solo el pasado.

La asociación bruta del equipo local con el target es V=0.171 y la del visitante V=0.183; no implican causalidad.

![Rendimiento histórico de equipos](figures/05_team_performance.png)

## 6. Relaciones entre variables y target

En 2025-26, tiros y tiros a puerta se relacionan con goles y resultado, como cabe esperar. Esa relación es **descriptiva y posterior al evento**: usarla para predecir el mismo partido produciría leakage crítico.

Las cuotas de apertura sí existen antes del partido y muestran señal predictiva. Su uso es viable si la aplicación garantiza la misma fuente y momento de captura. Las cuotas de cierre tienen riesgo temporal porque pueden no estar disponibles cuando se solicita la predicción.

![Correlaciones detalladas](figures/07_detailed_correlation_heatmap.png)

![Relaciones con el target](figures/08_relationships_with_target.png)

![Baseline de mercado](figures/09_market_baseline_confusion.png)

## 7. Riesgo de leakage

Se deben excluir del entrenamiento prepartido del mismo encuentro:

- Marcador final y al descanso, resultado al descanso y todas sus derivadas.
- Tiros, tiros a puerta, faltas, córners y tarjetas.
- `total_goals`, diferencias, clean sheets, puntos, over 2,5 y ambos marcan.
- Metadatos de fuente/cobertura, que revelan la temporada y el mecanismo de captura.
- `match_id`, que no tiene valor predictivo generalizable.

La fecha, temporada y equipos son inputs disponibles, pero no deben transformarse usando datos futuros. Las cuotas de cierre quedan condicionadas a definir la ventana de inferencia.

## 8. Viabilidad para una aplicación

Inputs directamente solicitables: equipo local, visitante, fecha/hora y, si existe una integración externa aprobada, cuotas prepartido. Para ofrecer valor sin depender de casas de apuestas, el pipeline debería generar forma reciente, fuerza ofensiva/defensiva y rating histórico a partir de partidos anteriores.

No son inputs aceptables: goles, tiros, tarjetas o cualquier estadística ocurrida durante/después del partido que se intenta predecir.

## 9. Reglas comunes propuestas

1. Mantener ambos CSV raw inmutables y verificar sus SHA-256.
2. Deduplicar por fecha + local + visitante y priorizar la fila detallada.
3. Normalizar fechas, temporada y tipos con el loader común.
4. No imputar el bloque detallado sobre 1995-96–2024-25: es ausencia estructural.
5. Excluir leakage y metadatos antes de modelar.
6. Construir features históricas con `shift`/ventanas cerradas al pasado.
7. Usar un split temporal; no congelarlo hasta aprobar T-0.4.
8. Proteger el test final y ajustar transformaciones solo con train.

## 10. Limitaciones y decisiones pendientes

- Falta confirmar y documentar URL de origen y licencia de los dos CSV.
- El target, el usuario y la ventana de predicción son propuestas que requieren aprobación del equipo.
- El bloque detallado representa una única temporada y no permite asumir estabilidad histórica.
- Las primeras temporadas contienen más partidos por cambios de tamaño de la liga; comparar conteos brutos sin normalizar puede inducir a error.
- No se han creado splits ni entrenado modelos: hacerlo antes de T-0.4 y del gate `Data Ready` contradiría `.specify`.

## Reproducibilidad

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-eda.txt
.\.venv\Scripts\python.exe scripts\run_laliga_eda.py
.\.venv\Scripts\python.exe scripts\create_eda_notebook.py
.\.venv\Scripts\python.exe scripts\execute_eda_notebook.py
.\.venv\Scripts\python.exe -m pytest
```

Los artefactos métricos se guardan en `reports/metrics/`, las figuras en `reports/figures/` y el dataset procesado local en `data/processed/` (ignorado por Git).
