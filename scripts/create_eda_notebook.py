"""Genera el notebook ejecutable del EDA desde el dataset procesado."""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf


FIGURES = [
    ("01_target_distribution.png", "La victoria local es la clase mayoritaria; el desbalance es moderado. La accuracy debe acompañarse de métricas por clase cuando T-0.4 apruebe el protocolo."),
    ("02_target_by_season.png", "La mezcla H/D/A varía entre temporadas. Aunque la asociación global es baja, el orden temporal debe preservarse para no evaluar con información futura."),
    ("03_goals_distribution.png", "Los goles son discretos y presentan cola derecha. Las goleadas son raras pero plausibles, por lo que no se eliminan solo por superar un umbral IQR."),
    ("04_home_advantage_trend.png", "La ventaja local fluctúa con el tiempo. Esto sugiere cambio de distribución y refuerza la necesidad futura de validación cronológica."),
    ("05_team_performance.png", "Los equipos muestran diferencias históricas, pero su identidad bruta puede generalizar mal ante ascensos/descensos; ratings y forma pasada serían alternativas más robustas."),
    ("06_missingness_profile.png", "Los nulos se concentran en estadísticas disponibles solo en 2025/26. Son estructurales y no deben imputarse sobre temporadas que nunca capturaron esas variables."),
    ("07_detailed_correlation_heatmap.png", "Tiros y tiros a puerta se correlacionan con goles, pero ocurren durante el partido. Esta señal es descriptiva y causaría leakage en una predicción prepartido."),
    ("08_relationships_with_target.png", "Las relaciones con el target confirman señal en cuotas y estadísticas postpartido. Solo las variables disponibles antes del encuentro podrían evaluarse como features."),
    ("09_market_baseline_confusion.png", "La regla del favorito de apertura conserva cierta señal, pero falla especialmente en empates. Es una referencia descriptiva sobre 2025/26, no un modelo ni una métrica final."),
    ("10_majority_baseline_confusion.png", "Predecir siempre H consigue una accuracy aparente aceptable pero recall cero en D y A. La matriz evidencia por qué una sola métrica agregada sería insuficiente."),
    ("11_outlier_profile.png", "El IQR se usa para identificar extremos, no para borrarlos automáticamente. La limpieza solo retira errores lógicos; los eventos deportivos raros permanecen."),
]


def main() -> None:
    cells = [
        nbf.v4.new_markdown_cell(
            "# EDA reproducible — LaLiga\n\n"
            "El análisis consume exclusivamente `data/processed/laliga_matches_clean.csv`, generado "
            "por `notebooks/00_laliga_preprocessing.ipynb` y el pipeline de `src/data/`. El target "
            "provisional es `result_ft` (H/D/A). No se entrenan modelos ni se crean particiones."
        ),
        nbf.v4.new_code_cell(
            "from pathlib import Path\n"
            "import sys\n"
            "import pandas as pd\n"
            "from IPython.display import Image, display\n\n"
            "PROJECT_ROOT = Path('..').resolve()\n"
            "if str(PROJECT_ROOT) not in sys.path:\n"
            "    sys.path.insert(0, str(PROJECT_ROOT))\n\n"
            "from src.data.laliga_loader import audit_dataset, load_processed_dataset\n"
            "from src.data.laliga_eda import build_data_dictionary, calculate_eda_metrics\n"
            "DATA_PATH = PROJECT_ROOT / 'data' / 'processed' / 'laliga_matches_clean.csv'\n"
            "FIGURES_DIR = PROJECT_ROOT / 'reports' / 'figures'\n"
            "matches = load_processed_dataset(DATA_PATH)\n"
            "metrics = calculate_eda_metrics(matches)\n"
            "pd.Series(audit_dataset(matches), name='valor').to_frame()"
        ),
        nbf.v4.new_markdown_cell(
            "## Calidad, nulos y duplicados\n\n"
            "La auditoría exige identificadores únicos, target completo y coherencia entre resultado "
            "y marcador final. Los nulos restantes se describen por columna y se interpretan según "
            "su mecanismo de captura."
        ),
        nbf.v4.new_code_cell(
            "missing = pd.DataFrame({'nulos': matches.isna().sum(), "
            "'porcentaje': matches.isna().mean()}).sort_values('porcentaje', ascending=False)\n"
            "missing.loc[missing['nulos'].gt(0)].head(30)"
        ),
        nbf.v4.new_markdown_cell(
            "## Distribuciones y target\n\n"
            "Se estudian balance, evolución temporal, goles y ventaja local. Estos análisis son "
            "descriptivos; no establecen causalidad."
        ),
        nbf.v4.new_code_cell(
            "pd.DataFrame({'partidos': pd.Series(metrics['target']['counts']), "
            "'proporción': pd.Series(metrics['target']['shares'])})"
        ),
        nbf.v4.new_markdown_cell(
            "## Outliers mediante IQR\n\n"
            "Se reportan Q1, Q3, límites y porcentaje de observaciones fuera de rango. Un outlier "
            "estadístico no equivale a un error de datos."
        ),
        nbf.v4.new_code_cell(
            "pd.DataFrame(metrics['outliers_iqr']).T.sort_values('pct', ascending=False)"
        ),
        nbf.v4.new_markdown_cell(
            "## Diccionario, correlaciones y leakage\n\n"
            "La disponibilidad en inferencia se documenta por variable. Goles, tiros, faltas, "
            "córners y tarjetas del mismo partido son postevento y deben excluirse de cualquier "
            "pipeline prepartido."
        ),
        nbf.v4.new_code_cell(
            "dictionary = build_data_dictionary(matches)\n"
            "dictionary[['column', 'role', 'available_at_inference', 'leakage_risk', "
            "'missing_pct']].head(60)"
        ),
        nbf.v4.new_markdown_cell(
            "## Matrices de confusión descriptivas\n\n"
            "Se comparan dos reglas fijas: predecir siempre la clase mayoritaria y elegir el favorito "
            "según cuotas promedio de apertura. No existe entrenamiento, split ni candidato de modelo."
        ),
        nbf.v4.new_code_cell(
            "labels = ['H', 'D', 'A']\n"
            "display(pd.DataFrame(metrics['target']['majority_confusion_matrix'], "
            "index=[f'Real {x}' for x in labels], columns=[f'Pred {x}' for x in labels]))\n"
            "display(pd.DataFrame(metrics['market_baseline']['confusion_matrix'], "
            "index=[f'Real {x}' for x in labels], columns=[f'Favorito {x}' for x in labels]))"
        ),
        nbf.v4.new_markdown_cell("## Gráficas persistentes e interpretación"),
    ]
    for filename, conclusion in FIGURES:
        cells.extend(
            [
                nbf.v4.new_code_cell(
                    f"display(Image(filename=str(FIGURES_DIR / '{filename}'), width=900))"
                ),
                nbf.v4.new_markdown_cell(f"**Conclusión — `{filename}`:** {conclusion}"),
            ]
        )
    cells.append(
        nbf.v4.new_markdown_cell(
            "## Conclusiones generales\n\n"
            "El dataset limpio es adecuado para EDA y conserva 31 temporadas. Antes de modelar deben "
            "aprobarse licencia, target, métricas y partición temporal. Las variables postpartido "
            "tienen leakage crítico; una aplicación prepartido debería usar fecha, equipos, cuotas "
            "capturadas a tiempo y features históricas calculadas solo con encuentros anteriores."
        )
    )
    notebook = nbf.v4.new_notebook(cells=cells)
    notebook["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"},
    }
    output = Path("notebooks/01_laliga_eda.ipynb")
    output.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, output)


if __name__ == "__main__":
    main()
