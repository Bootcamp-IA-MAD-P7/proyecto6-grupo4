"""Genera el notebook de navegación del EDA a partir del código compartido."""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf


def main() -> None:
    notebook = nbf.v4.new_notebook()
    notebook["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"},
    }
    notebook["cells"] = [
        nbf.v4.new_markdown_cell(
            "# EDA reproducible — LaLiga\n\n"
            "Este notebook es la puerta de entrada interactiva a T-1.3. La lógica vive en "
            "`src/data/` para evitar una segunda implementación incompatible. El informe completo "
            "se genera en `reports/laliga_eda.md`."
        ),
        nbf.v4.new_markdown_cell(
            "## Supuesto de trabajo\n\n"
            "Target provisional: `result_ft` (H/D/A). Ventana asumida: predicción antes del partido. "
            "La aprobación de equipo y la licencia de origen siguen pendientes; este notebook no cierra `Data Ready`."
        ),
        nbf.v4.new_code_cell(
            "from pathlib import Path\n"
            "import sys\n"
            "import pandas as pd\n"
            "from IPython.display import Image, display\n\n"
            "PROJECT_ROOT = Path('..').resolve()\n"
            "if str(PROJECT_ROOT) not in sys.path:\n"
            "    sys.path.insert(0, str(PROJECT_ROOT))\n\n"
            "from src.data.laliga_loader import load_raw_sources, build_canonical_dataset, audit_dataset\n"
            "from src.data.laliga_eda import calculate_eda_metrics, build_data_dictionary"
        ),
        nbf.v4.new_code_cell(
            "historical, detailed = load_raw_sources(Path('../data/raw'))\n"
            "matches = build_canonical_dataset(historical, detailed)\n"
            "pd.Series(audit_dataset(matches), name='value')"
        ),
        nbf.v4.new_code_cell(
            "target = matches['result_ft'].value_counts().rename(index={'H':'Victoria local','D':'Empate','A':'Victoria visitante'})\n"
            "pd.DataFrame({'count': target, 'share': target / len(matches)})"
        ),
        nbf.v4.new_code_cell(
            "missing = matches.isna().mean().sort_values(ascending=False).rename('missing_pct')\n"
            "missing[missing.gt(0)].to_frame().head(25)"
        ),
        nbf.v4.new_code_cell(
            "dictionary = build_data_dictionary(matches)\n"
            "dictionary[['column','role','available_at_inference','leakage_risk','missing_pct']].head(60)"
        ),
        nbf.v4.new_markdown_cell("## Evidencia visual generada"),
        nbf.v4.new_code_cell(
            "for figure in sorted(Path('../reports/figures').glob('*.png')):\n"
            "    print(figure.name)\n"
            "    display(Image(filename=str(figure), width=900))"
        ),
        nbf.v4.new_markdown_cell(
            "## Conclusión\n\n"
            "Las variables postpartido deben excluirse del modelado prepartido. Se recomienda un split temporal "
            "y features de forma construidas solo con el pasado. Consulte `reports/laliga_eda.md` para la interpretación completa."
        ),
    ]
    output = Path("notebooks/01_laliga_eda.ipynb")
    output.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, output)


if __name__ == "__main__":
    main()
