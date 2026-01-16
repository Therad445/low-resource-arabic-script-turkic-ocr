from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

def read_yaml(path: str | Path) -> Dict[str, Any]:
    """
    Tiny YAML loader wrapper. Requires PyYAML installed.
    """
    import yaml  # type: ignore

    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

@dataclass(frozen=True)
class ProjectConfig:
    name: str
    run_name: str

def get_project_cfg(cfg: Dict[str, Any]) -> ProjectConfig:
    prj = cfg.get("project", {}) or {}
    return ProjectConfig(
        name=str(prj.get("name", "arabic-script-turkic-ocr")),
        run_name=str(prj.get("run_name", "run")),
    )
