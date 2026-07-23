"""Genera el notebook reproducible de trazabilidad, limpieza y combinación."""

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
            "# Pipeline de preprocesamiento reproducible — LaLiga\n\n"
            "Este notebook documenta la procedencia, el contrato de columnas, la limpieza y la "
            "unión de los dos CSV originales. Los archivos de `data/raw/` se leen sin modificarlos; "
            "la única salida tabular se guarda en `data/processed/laliga_matches_clean.csv`."
        ),
        nbf.v4.new_code_cell(
            "from pathlib import Path\n"
            "import sys\n"
            "import pandas as pd\n"
            "from IPython.display import display\n\n"
            "PROJECT_ROOT = Path('..').resolve()\n"
            "if str(PROJECT_ROOT) not in sys.path:\n"
            "    sys.path.insert(0, str(PROJECT_ROOT))\n\n"
            "from src.data.laliga_loader import (\n"
            "    SOURCE_PROVENANCE, audit_dataset, build_source_column_policy,\n"
            "    file_sha256, load_processed_dataset, load_raw_sources,\n"
            "    preprocess_sources,\n"
            ")\n"
            "RAW_DIR = PROJECT_ROOT / 'data' / 'raw'\n"
            "PROCESSED_PATH = PROJECT_ROOT / 'data' / 'processed' / 'laliga_matches_clean.csv'"
        ),
        nbf.v4.new_markdown_cell(
            "## 1. Fuentes y huellas\n\n"
            "- `LaLiga_Matches.csv`: consolidado histórico identificado en Kaggle; la ficha atribuye "
            "los archivos a sus autores originales y se registra Football-Data como fuente aguas arriba.\n"
            "- `laliga_2025_2026_stats.csv`: instantánea del CSV `SP1.csv` de Football-Data para 2025/26.\n\n"
            "La licencia/condición de reutilización requiere aprobación del equipo y por eso el gate "
            "`Data Ready` permanece abierto."
        ),
        nbf.v4.new_code_cell(
            "provenance = pd.DataFrame.from_dict(SOURCE_PROVENANCE, orient='index')\n"
            "provenance.index.name = 'archivo_raw'\n"
            "display(provenance[['source_name', 'publisher', 'source_page_url', 'acquisition', "
            "'license', 'license_status']])\n"
            "pd.DataFrame([\n"
            "    {'archivo': path.name, 'bytes': path.stat().st_size, 'sha256': file_sha256(path)}\n"
            "    for path in sorted(RAW_DIR.glob('*.csv'))\n"
            "])"
        ),
        nbf.v4.new_markdown_cell(
            "## 2. Perfil previo a la limpieza\n\n"
            "Se comprueban dimensiones, duplicados exactos y nulos antes de transformar. Los nulos "
            "de descanso son opcionales; los campos críticos para identificar y etiquetar el partido "
            "son fecha, equipos, goles finales y resultado final."
        ),
        nbf.v4.new_code_cell(
            "historical, detailed = load_raw_sources(RAW_DIR)\n"
            "pd.DataFrame([\n"
            "    {'archivo': 'LaLiga_Matches.csv', 'filas': len(historical), "
            "'columnas': historical.shape[1], 'duplicados_exactos': historical.duplicated().sum(), "
            "'celdas_nulas': historical.isna().sum().sum()},\n"
            "    {'archivo': 'laliga_2025_2026_stats.csv', 'filas': len(detailed), "
            "'columnas': detailed.shape[1], 'duplicados_exactos': detailed.duplicated().sum(), "
            "'celdas_nulas': detailed.isna().sum().sum()},\n"
            "])"
        ),
        nbf.v4.new_markdown_cell(
            "## 3. Política completa de columnas\n\n"
            "El histórico conserva sus campos de identificación, marcador y resultado. En el archivo "
            "detallado se conservan 39 columnas: identidad/tiempo, marcador, estadísticas agregadas y "
            "promedios de mercado. Se descartan cuotas por casa, máximas y de exchange porque son "
            "redundantes respecto de los promedios, elevan la dimensionalidad y tienen cobertura irregular."
        ),
        nbf.v4.new_code_cell(
            "column_policy = build_source_column_policy(historical, detailed)\n"
            "display(column_policy.groupby(['source_file', 'action']).size().rename('columnas').to_frame())\n"
            "column_policy"
        ),
        nbf.v4.new_markdown_cell(
            "## 4. Limpieza y criterio de combinación\n\n"
            "Reglas: recortar texto, normalizar H/D/A, convertir fecha y goles, retirar duplicados "
            "exactos, retirar filas inequívocamente inválidas y deduplicar cada fuente por "
            "`fecha normalizada + local + visitante`. Después se hace una unión vertical. Cuando "
            "ambas fuentes contienen el mismo partido se conserva la fila detallada porque incluye "
            "el bloque mínimo del histórico y añade estadísticas/cuotas promedio."
        ),
        nbf.v4.new_code_cell(
            "clean, preprocessing = preprocess_sources(historical, detailed)\n"
            "display(pd.DataFrame(preprocessing['source_cleaning']).T)\n"
            "display(pd.Series(preprocessing['join'], name='valor').to_frame())\n"
            "pd.Series(audit_dataset(clean), name='resultado').to_frame()"
        ),
        nbf.v4.new_markdown_cell(
            "## 5. Persistencia y verificación de la salida\n\n"
            "Los nulos del bloque detallado en temporadas históricas se mantienen: representan "
            "ausencia estructural, no un dato perdido imputable. Los dos registros con descanso "
            "incompleto también se conservan porque esas variables son opcionales y postpartido."
        ),
        nbf.v4.new_code_cell(
            "PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)\n"
            "clean.to_csv(PROCESSED_PATH, index=False, encoding='utf-8', date_format='%Y-%m-%d')\n"
            "reloaded = load_processed_dataset(PROCESSED_PATH)\n"
            "reloaded_audit = audit_dataset(reloaded)\n"
            "pd.DataFrame({\n"
            "    'control': ['ruta', 'filas', 'columnas', 'sha256', 'duplicados_id', 'target_nulo'],\n"
            "    'valor': [str(PROCESSED_PATH.relative_to(PROJECT_ROOT)), len(reloaded), "
            "reloaded.shape[1], file_sha256(PROCESSED_PATH), "
            "reloaded_audit['duplicate_match_ids'], reloaded_audit['missing_target']],\n"
            "})"
        ),
        nbf.v4.new_markdown_cell(
            "## Conclusión\n\n"
            "La salida contiene una fila por partido y un esquema canónico único. La prioridad de la "
            "fuente detallada evita duplicar los encuentros compartidos y conserva la máxima información. "
            "No se imputan ausencias estructurales ni se eliminan partidos deportivos extremos que sean "
            "lógicamente válidos."
        ),
    ]
    output = Path("notebooks/00_laliga_preprocessing.ipynb")
    output.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, output)


if __name__ == "__main__":
    main()
