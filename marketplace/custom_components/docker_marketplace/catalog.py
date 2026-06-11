"""Catalog management for Docker Marketplace."""
from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .const import CATEGORIES, CATEGORY_ICONS, DEFAULT_CATALOG_PATH

_LOGGER = logging.getLogger(__name__)


@dataclass
class AppPort:
    """Port mapping for an app."""

    container: int
    host: int
    protocol: str = "tcp"
    description: str = ""


@dataclass
class AppVolume:
    """Volume mapping for an app."""

    name: str
    container: str
    description: str = ""
    required: bool = False
    default_host: str = ""


@dataclass
class AppEnvironment:
    """Environment variable for an app."""

    name: str
    default: str = ""
    description: str = ""
    required: bool = False
    secret: bool = False


@dataclass
class AppRequirements:
    """Requirements for an app."""

    min_memory: int = 0  # MB
    recommended_memory: int = 0  # MB
    gpu: str = "none"  # none, optional, required
    ports_available: list[int] = field(default_factory=list)


@dataclass
class AppCompose:
    """Docker compose configuration."""

    image: str
    restart: str = "unless-stopped"
    network_mode: str | None = None
    privileged: bool = False
    devices: list[str] = field(default_factory=list)
    cap_add: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class AppDefinition:
    """Application definition from catalog."""

    id: str
    name: str
    category: str
    description: str
    icon: str = "mdi:docker"
    logo: str = ""
    version: str = "latest"
    maintainer: str = ""
    website: str = ""
    documentation: str = ""
    requirements: AppRequirements = field(default_factory=AppRequirements)
    ports: list[AppPort] = field(default_factory=list)
    volumes: list[AppVolume] = field(default_factory=list)
    environment: list[AppEnvironment] = field(default_factory=list)
    compose: AppCompose | None = None
    compose_file: str = ""  # Path to external docker-compose.yml
    compose_raw: dict[str, Any] | None = None  # Raw docker-compose content for multi-service stacks
    depends_on: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass
class CategoryDefinition:
    """Category definition."""

    id: str
    name: str
    icon: str
    description: str = ""


class Catalog:
    """App catalog manager."""

    def __init__(self, catalog_path: str = DEFAULT_CATALOG_PATH) -> None:
        """Initialize catalog."""
        self._catalog_path = Path(catalog_path)
        self._apps: dict[str, AppDefinition] = {}
        self._categories: dict[str, CategoryDefinition] = {}
        self._loaded = False

    @property
    def apps(self) -> dict[str, AppDefinition]:
        """Return all apps."""
        return self._apps

    @property
    def categories(self) -> dict[str, CategoryDefinition]:
        """Return all categories."""
        return self._categories

    async def load(self) -> bool:
        """Load catalog from disk."""
        try:
            # Initialize default categories
            self._init_default_categories()

            # Load main catalog file
            catalog_file = self._catalog_path / "catalog.yaml"
            if catalog_file.exists():
                await self._load_catalog_file(catalog_file)

            # Load individual app files
            apps_dir = self._catalog_path / "apps"
            if apps_dir.exists():
                for app_file in apps_dir.glob("*.yaml"):
                    await self._load_app_file(app_file)

            self._loaded = True
            _LOGGER.info(
                "Loaded catalog with %d apps in %d categories",
                len(self._apps),
                len(self._categories),
            )
            return True
        except Exception as err:
            _LOGGER.error("Error loading catalog: %s", err)
            return False

    def _init_default_categories(self) -> None:
        """Initialize default categories."""
        category_names = {
            "media": "Media",
            "gaming": "Gaming",
            "download": "Download",
            "smart_home": "Smart Home",
            "security": "Security",
            "network": "Network",
            "ai": "AI & ML",
            "monitoring": "Monitoring",
            "backup": "Backup",
            "web": "Web",
        }

        for cat_id in CATEGORIES:
            self._categories[cat_id] = CategoryDefinition(
                id=cat_id,
                name=category_names.get(cat_id, cat_id.title()),
                icon=CATEGORY_ICONS.get(cat_id, "mdi:folder"),
            )

    async def _load_catalog_file(self, catalog_file: Path) -> None:
        """Load main catalog file."""
        try:
            data = await asyncio.to_thread(self._read_yaml_file, catalog_file)

            if not data:
                return

            # Load custom categories
            if "categories" in data:
                for cat_data in data["categories"]:
                    cat = CategoryDefinition(
                        id=cat_data["id"],
                        name=cat_data.get("name", cat_data["id"]),
                        icon=cat_data.get("icon", "mdi:folder"),
                        description=cat_data.get("description", ""),
                    )
                    self._categories[cat.id] = cat

            # Load inline apps
            if "apps" in data:
                for app_data in data["apps"]:
                    app = self._parse_app(app_data)
                    if app:
                        self._apps[app.id] = app

        except Exception as err:
            _LOGGER.error("Error loading catalog file %s: %s", catalog_file, err)

    async def _load_app_file(self, app_file: Path) -> None:
        """Load individual app file."""
        try:
            data = await asyncio.to_thread(self._read_yaml_file, app_file)

            if not data:
                return

            app = self._parse_app(data)
            if app:
                self._apps[app.id] = app
                _LOGGER.debug("Loaded app %s from %s", app.id, app_file)

        except Exception as err:
            _LOGGER.error("Error loading app file %s: %s", app_file, err)

    def _read_yaml_file(self, file_path: Path) -> dict[str, Any] | None:
        """Read and parse a YAML file (blocking, run in thread)."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception:
            return None

    def _parse_app(self, data: dict[str, Any]) -> AppDefinition | None:
        """Parse app data into AppDefinition."""
        try:
            app_id = data.get("id")
            if not app_id:
                _LOGGER.warning("App missing required 'id' field")
                return None

            # Parse requirements
            req_data = data.get("requirements", {})
            requirements = AppRequirements(
                min_memory=req_data.get("min_memory", 0),
                recommended_memory=req_data.get("recommended_memory", 0),
                gpu=req_data.get("gpu", "none"),
            )

            # Parse ports
            ports = []
            for port_data in data.get("ports", []):
                ports.append(
                    AppPort(
                        container=port_data["container"],
                        host=port_data.get("host", port_data["container"]),
                        protocol=port_data.get("protocol", "tcp"),
                        description=port_data.get("description", ""),
                    )
                )

            # Parse volumes
            volumes = []
            for vol_data in data.get("volumes", []):
                volumes.append(
                    AppVolume(
                        name=vol_data["name"],
                        container=vol_data["container"],
                        description=vol_data.get("description", ""),
                        required=vol_data.get("required", False),
                        default_host=vol_data.get("default_host", ""),
                    )
                )

            # Parse environment
            environment = []
            for env_data in data.get("environment", []):
                environment.append(
                    AppEnvironment(
                        name=env_data["name"],
                        default=str(env_data.get("default", "")),
                        description=env_data.get("description", ""),
                        required=env_data.get("required", False),
                        secret=env_data.get("secret", False),
                    )
                )

            # Parse compose
            compose = None
            if "compose" in data:
                comp_data = data["compose"]
                compose = AppCompose(
                    image=comp_data["image"],
                    restart=comp_data.get("restart", "unless-stopped"),
                    network_mode=comp_data.get("network_mode"),
                    privileged=comp_data.get("privileged", False),
                    devices=comp_data.get("devices", []),
                    cap_add=comp_data.get("cap_add", []),
                )

            return AppDefinition(
                id=app_id,
                name=data.get("name", app_id),
                category=data.get("category", "other"),
                description=data.get("description", ""),
                icon=data.get("icon", "mdi:docker"),
                logo=data.get("logo", ""),
                version=data.get("version", "latest"),
                maintainer=data.get("maintainer", ""),
                website=data.get("website", ""),
                documentation=data.get("documentation", ""),
                requirements=requirements,
                ports=ports,
                volumes=volumes,
                environment=environment,
                compose=compose,
                compose_file=data.get("compose_file", ""),
                compose_raw=data.get("compose_raw"),
                depends_on=data.get("depends_on", []),
                tags=data.get("tags", []),
            )

        except Exception as err:
            _LOGGER.error("Error parsing app data: %s", err)
            return None

    def get_app(self, app_id: str) -> AppDefinition | None:
        """Get app by ID."""
        return self._apps.get(app_id)

    def get_apps_by_category(self, category: str) -> list[AppDefinition]:
        """Get all apps in a category."""
        return [app for app in self._apps.values() if app.category == category]

    def search_apps(self, query: str) -> list[AppDefinition]:
        """Search apps by name, description, or tags."""
        query_lower = query.lower()
        results = []

        for app in self._apps.values():
            if (
                query_lower in app.name.lower()
                or query_lower in app.description.lower()
                or any(query_lower in tag.lower() for tag in app.tags)
            ):
                results.append(app)

        return results

    def to_dict(self) -> dict[str, Any]:
        """Convert catalog to dictionary for API responses."""
        return {
            "categories": [
                {
                    "id": cat.id,
                    "name": cat.name,
                    "icon": cat.icon,
                    "description": cat.description,
                    "app_count": len(self.get_apps_by_category(cat.id)),
                }
                for cat in self._categories.values()
            ],
            "apps": [
                {
                    "id": app.id,
                    "name": app.name,
                    "category": app.category,
                    "description": app.description,
                    "icon": app.icon,
                    "logo": app.logo,
                    "version": app.version,
                    "tags": app.tags,
                    "requirements": {
                        "min_memory": app.requirements.min_memory,
                        "recommended_memory": app.requirements.recommended_memory,
                        "gpu": app.requirements.gpu,
                    },
                    "ports": [
                        {
                            "container": p.container,
                            "host": p.host,
                            "protocol": p.protocol,
                            "description": p.description,
                        }
                        for p in app.ports
                    ],
                    "environment": [
                        {
                            "name": e.name,
                            "default": e.default,
                            "description": e.description,
                            "required": e.required,
                            "secret": e.secret,
                        }
                        for e in app.environment
                    ],
                }
                for app in self._apps.values()
            ],
        }

    def app_to_dict(self, app_id: str) -> dict[str, Any] | None:
        """Convert single app to detailed dictionary."""
        app = self.get_app(app_id)
        if not app:
            return None

        return {
            "id": app.id,
            "name": app.name,
            "category": app.category,
            "description": app.description,
            "icon": app.icon,
            "logo": app.logo,
            "version": app.version,
            "maintainer": app.maintainer,
            "website": app.website,
            "documentation": app.documentation,
            "requirements": {
                "min_memory": app.requirements.min_memory,
                "recommended_memory": app.requirements.recommended_memory,
                "gpu": app.requirements.gpu,
            },
            "ports": [
                {
                    "container": p.container,
                    "host": p.host,
                    "protocol": p.protocol,
                    "description": p.description,
                }
                for p in app.ports
            ],
            "volumes": [
                {
                    "name": v.name,
                    "container": v.container,
                    "description": v.description,
                    "required": v.required,
                }
                for v in app.volumes
            ],
            "environment": [
                {
                    "name": e.name,
                    "default": e.default,
                    "description": e.description,
                    "required": e.required,
                    "secret": e.secret,
                }
                for e in app.environment
            ],
            "depends_on": app.depends_on,
            "tags": app.tags,
        }
