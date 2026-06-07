from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

HUMAN_CONFIRM = "需要人工确认"


@dataclass
class ProductLink:
    url: str
    source_platform: str = "unknown"


@dataclass
class RawProduct:
    url: str
    source_platform: str
    title: str = HUMAN_CONFIRM
    description: str = HUMAN_CONFIRM
    images: list[str] = field(default_factory=list)
    sku_specs: list[dict[str, Any]] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)
    price: str = HUMAN_CONFIRM
    category: str = HUMAN_CONFIRM
    warnings: list[str] = field(default_factory=list)


@dataclass
class ListingVersion:
    account: str
    target_platform: str
    url: str
    title: str
    description: str
    bullet_points: list[str]
    sku: str
    spec_name: str
    spec_value: str
    color: str
    size: str
    material: str
    quantity: str
    weight: str
    package_size: str
    price: str
    category_id: str
    attributes: dict[str, Any]
    stock: int
    logistics: str
    main_image: str
    gallery_images: list[str]
    detail_images: list[str]
    flags: list[str] = field(default_factory=list)


@dataclass
class ImageAsset:
    source_url: str
    output_path: Path
    risk_level: str
    reason: str
    role: str
