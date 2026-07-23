"""Carga, auditoría y preparación común de datos."""

from .laliga_loader import (
    DETAILED_FILENAME,
    HISTORICAL_FILENAME,
    SOURCE_PROVENANCE,
    audit_dataset,
    build_canonical_dataset,
    build_dataset_manifest,
    build_source_column_policy,
    load_processed_dataset,
    load_raw_sources,
    preprocess_sources,
    write_canonical_outputs,
)

__all__ = [
    "DETAILED_FILENAME",
    "HISTORICAL_FILENAME",
    "SOURCE_PROVENANCE",
    "audit_dataset",
    "build_canonical_dataset",
    "build_dataset_manifest",
    "build_source_column_policy",
    "load_processed_dataset",
    "load_raw_sources",
    "preprocess_sources",
    "write_canonical_outputs",
]
