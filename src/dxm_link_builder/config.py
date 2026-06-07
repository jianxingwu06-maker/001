from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

DEFAULT_RULES_PATH = Path(__file__).resolve().parents[2] / "config" / "platform_rules.json"


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


class PlatformRules:
    def __init__(self, rules_path: Path | str = DEFAULT_RULES_PATH):
        self.rules_path = Path(rules_path)
        self.raw = json.loads(self.rules_path.read_text(encoding="utf-8"))

    def get(self, platform: str) -> dict[str, Any]:
        default = self.raw.get("default", {})
        specific = self.raw.get(platform.lower(), {})
        return deep_merge(default, specific)
