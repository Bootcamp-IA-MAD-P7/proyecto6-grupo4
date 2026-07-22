"""Ejecuta el notebook del EDA y guarda sus salidas para revisión."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

import nbformat
from nbclient import NotebookClient


def main() -> None:
    project_root = Path.cwd()
    os.environ["IPYTHONDIR"] = str(project_root / ".ipython")
    os.environ["JUPYTER_RUNTIME_DIR"] = str(project_root / ".jupyter_runtime")
    if hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    notebook_path = Path("notebooks/01_laliga_eda.ipynb")
    notebook = nbformat.read(notebook_path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=180,
        kernel_name="python3",
        resources={"metadata": {"path": str(notebook_path.parent)}},
    )
    client.execute()
    nbformat.write(notebook, notebook_path)


if __name__ == "__main__":
    main()
