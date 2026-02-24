from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

PROFILE_DIR = Path(__file__).resolve().parents[2] / "profiles"


def load_profile(name: str) -> dict[str, Any]:
    path = PROFILE_DIR / f"{name}.yaml"
    if not path.exists():
        raise ValueError(f"Unknown profile: {name}")
    with open(path, "r", encoding="utf-8") as f:
        profile = yaml.safe_load(f) or {}
    if not isinstance(profile, dict):
        raise ValueError("Profile must be an object")
    return profile
