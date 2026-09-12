"""Measurement-year package discovery, validation, and source precedence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


SOURCE_PRECEDENCE = ["SPECIFICATION", "MLD", "VSD", "SQL", "DECISION_TREE", "FAQ"]


class PackageError(ValueError):
    pass


class KnowledgePackageManager:
    def __init__(self, root: Path):
        self.root = root
        self.base = root / "knowledge_packages"
        self.registry = json.loads((self.base / "registry.json").read_text(encoding="utf-8"))

    def list_packages(self) -> list[dict]:
        return self.registry["packages"]

    def resolve(self, measure_id: str, measurement_year: int) -> Path:
        match = next((p for p in self.list_packages() if p["measure_id"] == measure_id and int(p["measurement_year"]) == int(measurement_year)), None)
        if not match:
            raise PackageError(f"No governed package is registered for {measure_id} MY{measurement_year}.")
        path = self.base / match["path"]
        manifest_path = path / "manifest.json"
        if not manifest_path.exists():
            raise PackageError(f"Package manifest is missing for {measure_id} MY{measurement_year}.")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("measure_id") != measure_id or int(manifest.get("measurement_year", 0)) != int(measurement_year):
            raise PackageError("The folder, registry, and manifest measurement year do not agree. Package rejected.")
        required = manifest.get("required_artifacts", [])
        missing = [name for name in required if not (path / name).exists()]
        if missing:
            raise PackageError("Package is incomplete: " + ", ".join(missing))
        return path

    def manifest(self, measure_id: str, measurement_year: int) -> dict:
        path = self.resolve(measure_id, measurement_year)
        return json.loads((path / "manifest.json").read_text(encoding="utf-8"))

    @staticmethod
    def source_winner(sources: list[dict]) -> dict | None:
        ranked = sorted(sources, key=lambda s: SOURCE_PRECEDENCE.index(s["type"]) if s["type"] in SOURCE_PRECEDENCE else 999)
        return ranked[0] if ranked else None

    @staticmethod
    def hash_file(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()
