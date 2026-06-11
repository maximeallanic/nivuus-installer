"""Data coordinator for Docker Marketplace."""
from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any
import shutil

import yaml
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .catalog import AppDefinition, Catalog
from .const import (
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    STATE_INSTALLING,
    STATE_NOT_INSTALLED,
    STATE_RUNNING,
    STATE_STOPPED,
    UPDATE_CHECK_INTERVAL,
)
from .docker_client import ContainerInfo, ContainerStats, DockerClient

_LOGGER = logging.getLogger(__name__)


@dataclass
class InstalledApp:
    """Information about an installed app."""

    app_id: str
    name: str
    container_name: str
    state: str
    image: str
    version: str
    compose_file: Path
    config: dict[str, Any] | None = None
    cpu_percent: float = 0.0
    memory_usage: int = 0
    memory_percent: float = 0.0
    local_digest: str | None = None
    remote_digest: str | None = None
    update_available: bool = False


@dataclass
class MarketplaceData:
    """Data from Docker Marketplace coordinator."""

    installed_apps: dict[str, InstalledApp]
    available_apps: dict[str, AppDefinition]
    container_stats: dict[str, ContainerStats]


class DockerMarketplaceCoordinator(DataUpdateCoordinator[MarketplaceData]):
    """Coordinator for Docker Marketplace data."""

    def __init__(
        self,
        hass: HomeAssistant,
        docker_client: DockerClient,
        catalog: Catalog,
        stacks_path: str,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.docker_client = docker_client
        self.catalog = catalog
        self.stacks_path = Path(stacks_path)
        self._installing: set[str] = set()
        self._last_update_check: float = 0.0
        self._update_cache: dict[str, tuple[str | None, str | None, bool]] = {}

        # Ensure stacks directory exists
        self.stacks_path.mkdir(parents=True, exist_ok=True)

    async def _async_update_data(self) -> MarketplaceData:
        """Fetch data from Docker."""
        try:
            installed_apps = await self._get_installed_apps()
            container_stats = {}

            # Get stats for running containers
            for app_id, app in installed_apps.items():
                if app.state == STATE_RUNNING:
                    stats = await self.docker_client.get_container_stats(
                        app.container_name
                    )
                    if stats:
                        container_stats[app_id] = stats
                        app.cpu_percent = stats.cpu_percent
                        app.memory_usage = stats.memory_usage
                        app.memory_percent = stats.memory_percent

            # Check for updates periodically
            await self._check_for_updates(installed_apps)

            return MarketplaceData(
                installed_apps=installed_apps,
                available_apps=self.catalog.apps,
                container_stats=container_stats,
            )
        except Exception as err:
            raise UpdateFailed(f"Error fetching Docker data: {err}") from err

    async def _check_for_updates(self, installed_apps: dict[str, InstalledApp]) -> None:
        """Check for updates for all installed apps."""
        current_time = time.time()

        # Only check updates every UPDATE_CHECK_INTERVAL
        if current_time - self._last_update_check < UPDATE_CHECK_INTERVAL:
            # Use cached values
            for app_id, app in installed_apps.items():
                if app_id in self._update_cache:
                    cached = self._update_cache[app_id]
                    app.local_digest = cached[0]
                    app.remote_digest = cached[1]
                    app.update_available = cached[2]
            return

        self._last_update_check = current_time
        _LOGGER.info("Checking for updates for %d apps", len(installed_apps))

        for app_id, app in installed_apps.items():
            if not app.image or app.image == "unknown":
                continue

            try:
                # Get local digest
                local_digest = await self.docker_client.get_local_image_digest(app.image)
                app.local_digest = local_digest

                # Get remote digest
                remote_digest = await self.docker_client.get_remote_image_digest(app.image)
                app.remote_digest = remote_digest

                # Compare digests
                if local_digest and remote_digest:
                    app.update_available = local_digest != remote_digest
                    if app.update_available:
                        _LOGGER.info(
                            "Update available for %s: %s -> %s",
                            app_id,
                            local_digest[:12] if local_digest else "unknown",
                            remote_digest[:12] if remote_digest else "unknown"
                        )
                else:
                    app.update_available = False

                # Cache the result
                self._update_cache[app_id] = (
                    app.local_digest,
                    app.remote_digest,
                    app.update_available,
                )

            except Exception as err:
                _LOGGER.debug("Error checking update for %s: %s", app_id, err)

    async def force_update_check(self) -> None:
        """Force an immediate update check."""
        self._last_update_check = 0.0
        await self.async_refresh()

    async def _get_installed_apps(self) -> dict[str, InstalledApp]:
        """Get all installed marketplace apps."""
        installed = {}

        # Scan stacks directory for installed apps
        if not self.stacks_path.exists():
            return installed

        # Get directory listing in thread to avoid blocking
        stack_dirs = await asyncio.to_thread(list, self.stacks_path.iterdir())

        for stack_dir in stack_dirs:
            if not stack_dir.is_dir():
                continue

            # Check for compose file (local or external reference)
            compose_file = stack_dir / "docker-compose.yml"
            compose_ref = stack_dir / "compose_ref.txt"

            if compose_ref.exists():
                # External compose file
                external_path = await asyncio.to_thread(compose_ref.read_text)
                compose_file = Path(external_path.strip())
                if not compose_file.exists():
                    continue
            elif not compose_file.exists():
                continue

            app_id = stack_dir.name

            # Check if this app is in the catalog
            app_def = self.catalog.get_app(app_id)

            # Get container state
            # For compose_raw apps (multi-service stacks), use project state
            container_name = self._get_container_name(app_id)

            if app_id in self._installing:
                state = STATE_INSTALLING
            elif app_def and app_def.compose_raw:
                # Multi-service stack: check by project name
                state = await self.docker_client.get_project_state(app_id)
            else:
                state = await self.docker_client.get_container_state(container_name)

            # Read compose file for image info
            image = "unknown"
            try:
                compose_data = await asyncio.to_thread(self._read_compose_file, compose_file)
                if compose_data:
                    services = compose_data.get("services", {})
                    if services:
                        first_service = list(services.values())[0]
                        image = first_service.get("image", "unknown")
            except Exception:
                pass

            # Load saved configuration
            config_file = stack_dir / "config.yaml"
            saved_config = None
            if config_file.exists():
                try:
                    saved_config = await asyncio.to_thread(self._read_config_file, config_file)
                except Exception:
                    pass

            installed[app_id] = InstalledApp(
                app_id=app_id,
                name=app_def.name if app_def else app_id,
                container_name=container_name,
                state=state,
                image=image,
                version=app_def.version if app_def else "unknown",
                compose_file=compose_file,
                config=saved_config,
            )

        return installed

    def _get_container_name(self, app_id: str) -> str:
        """Get container name for an app."""
        # Convention: same as app_id (set in _generate_compose)
        return app_id

    async def _get_compose_file(self, app_id: str) -> Path | None:
        """Get compose file path for an app (local or external)."""
        stack_dir = self.stacks_path / app_id
        compose_file = stack_dir / "docker-compose.yml"
        compose_ref = stack_dir / "compose_ref.txt"

        if compose_ref.exists():
            # External compose file
            external_path = await asyncio.to_thread(compose_ref.read_text)
            compose_file = Path(external_path.strip())

        if compose_file.exists():
            return compose_file
        return None

    async def install_app(
        self, app_id: str, config: dict[str, Any] | None = None
    ) -> bool:
        """Install an app from the catalog."""
        app_def = self.catalog.get_app(app_id)
        if not app_def:
            _LOGGER.error("App %s not found in catalog", app_id)
            return False

        # Check if app has compose config, external file, or raw compose
        if not app_def.compose and not app_def.compose_file and not app_def.compose_raw:
            _LOGGER.error("App %s has no compose configuration", app_id)
            return False

        _LOGGER.info("Installing app %s", app_id)
        self._installing.add(app_id)

        try:
            # Create stack directory
            stack_dir = self.stacks_path / app_id
            await asyncio.to_thread(stack_dir.mkdir, parents=True, exist_ok=True)

            # Save configuration
            config_file = stack_dir / "config.yaml"
            await asyncio.to_thread(self._write_config_file, config_file, config or {})

            # Generate .env file for environment variables
            env_file = stack_dir / ".env"
            await asyncio.to_thread(self._write_env_file, env_file, app_def, config or {})

            # Handle compose configuration: raw > external file > generated
            compose_file = stack_dir / "docker-compose.yml"

            if app_def.compose_raw:
                # Use raw compose content directly (multi-service stacks)
                await asyncio.to_thread(self._write_compose_file, compose_file, app_def.compose_raw)
                _LOGGER.info("Using raw compose content for %s", app_id)
            elif app_def.compose_file:
                # Use external compose file directly
                external_compose = Path(app_def.compose_file)
                if not external_compose.exists():
                    _LOGGER.error("External compose file not found: %s", app_def.compose_file)
                    return False
                compose_file = external_compose
                # Create a reference file in stack_dir
                ref_file = stack_dir / "compose_ref.txt"
                await asyncio.to_thread(ref_file.write_text, str(external_compose))
                _LOGGER.info("Using external compose file: %s", compose_file)
            else:
                # Generate docker-compose.yml from single-service definition
                compose_content = self._generate_compose(app_def, config)
                await asyncio.to_thread(self._write_compose_file, compose_file, compose_content)

            # Run docker compose up
            success = await self.docker_client.compose_up(
                compose_file, project_name=app_id
            )

            if success:
                _LOGGER.info("Successfully installed app %s", app_id)
                await self.async_refresh()
                return True
            else:
                _LOGGER.error("Failed to start app %s", app_id)
                return False

        except Exception as err:
            _LOGGER.error("Error installing app %s: %s", app_id, err)
            return False
        finally:
            self._installing.discard(app_id)

    async def remove_app(self, app_id: str, remove_data: bool = False) -> bool:
        """Remove an installed app."""
        stack_dir = self.stacks_path / app_id
        compose_file = await self._get_compose_file(app_id)

        if not compose_file:
            _LOGGER.warning("App %s not found", app_id)
            return False

        _LOGGER.info("Removing app %s", app_id)

        try:
            # Run docker compose down
            success = await self.docker_client.compose_down(
                compose_file, project_name=app_id, volumes=remove_data
            )

            if success:
                # Remove stack directory (but not external compose file)
                if stack_dir.exists():
                    await asyncio.to_thread(shutil.rmtree, stack_dir)
                _LOGGER.info("Successfully removed app %s", app_id)
                await self.async_refresh()
                return True
            else:
                _LOGGER.error("Failed to stop app %s", app_id)
                return False

        except Exception as err:
            _LOGGER.error("Error removing app %s: %s", app_id, err)
            return False

    async def update_app(self, app_id: str) -> bool:
        """Update an installed app (pull latest image and restart)."""
        compose_file = await self._get_compose_file(app_id)

        if not compose_file:
            _LOGGER.warning("App %s not found", app_id)
            return False

        _LOGGER.info("Updating app %s", app_id)

        try:
            # Pull latest images
            await self.docker_client.compose_pull(compose_file, project_name=app_id)

            # Recreate with the freshly pulled images: stop + remove + create + start,
            # so the new image and restart policy are actually applied (a plain
            # restart would keep the old image and could leave the container stopped).
            success = await self.docker_client.compose_up(
                compose_file, project_name=app_id, pull=False, recreate=True
            )

            if success:
                _LOGGER.info("Successfully updated app %s", app_id)
                await self.async_refresh()
                return True
            else:
                _LOGGER.error("Failed to update app %s", app_id)
                return False

        except Exception as err:
            _LOGGER.error("Error updating app %s: %s", app_id, err)
            return False

    async def start_app(self, app_id: str) -> bool:
        """Start an installed app."""
        compose_file = await self._get_compose_file(app_id)

        if not compose_file:
            _LOGGER.warning("App %s not found", app_id)
            return False

        success = await self.docker_client.compose_up(
            compose_file, project_name=app_id, pull=False
        )

        if success:
            await self.async_refresh()
        return success

    async def stop_app(self, app_id: str) -> bool:
        """Stop an installed app."""
        compose_file = await self._get_compose_file(app_id)

        if not compose_file:
            _LOGGER.warning("App %s not found", app_id)
            return False

        success = await self.docker_client.compose_down(
            compose_file, project_name=app_id, volumes=False
        )

        if success:
            await self.async_refresh()
        return success

    async def restart_app(self, app_id: str) -> bool:
        """Restart an installed app."""
        await self.stop_app(app_id)
        return await self.start_app(app_id)

    async def get_logs(self, app_id: str, tail: int = 100) -> str | None:
        """Get logs for an app."""
        container_name = self._get_container_name(app_id)
        return await self.docker_client.get_container_logs(container_name, tail)

    def _generate_compose(
        self, app_def: AppDefinition, config: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Generate docker-compose.yml content for an app."""
        config = config or {}

        # Build service definition
        service: dict[str, Any] = {
            "image": app_def.compose.image,
            "restart": app_def.compose.restart,
            "container_name": f"{app_def.id}",
        }

        # Network mode
        if app_def.compose.network_mode:
            service["network_mode"] = app_def.compose.network_mode

        # Privileged mode
        if app_def.compose.privileged:
            service["privileged"] = True

        # Devices
        if app_def.compose.devices:
            service["devices"] = app_def.compose.devices

        # Capabilities
        if app_def.compose.cap_add:
            service["cap_add"] = app_def.compose.cap_add

        # Ports
        if app_def.ports and not app_def.compose.network_mode:
            service["ports"] = []
            for port in app_def.ports:
                host_port = config.get(f"port_{port.container}", port.host)
                service["ports"].append(f"{host_port}:{port.container}/{port.protocol}")

        # Volumes
        if app_def.volumes:
            service["volumes"] = []
            for vol in app_def.volumes:
                host_path = config.get(f"volume_{vol.name}", vol.default_host)
                if not host_path:
                    # Use default path based on stacks directory
                    host_path = str(self.stacks_path / app_def.id / "data" / vol.name)
                service["volumes"].append(f"{host_path}:{vol.container}")

        # Environment variables
        if app_def.environment:
            service["environment"] = {}
            for env in app_def.environment:
                value = config.get(f"env_{env.name}", env.default)
                if value or env.required:
                    service["environment"][env.name] = value

        # Labels for identification
        service["labels"] = {
            "docker_marketplace.app_id": app_def.id,
            "docker_marketplace.managed": "true",
        }

        return {
            "version": "3.8",
            "services": {
                app_def.id: service,
            },
        }

    def get_installed_app(self, app_id: str) -> InstalledApp | None:
        """Get an installed app by ID."""
        if self.data:
            return self.data.installed_apps.get(app_id)
        return None

    def is_installed(self, app_id: str) -> bool:
        """Check if an app is installed."""
        if self.data:
            return app_id in self.data.installed_apps
        return False

    def _read_compose_file(self, compose_file: Path) -> dict[str, Any] | None:
        """Read and parse a compose file (blocking, run in thread)."""
        try:
            with open(compose_file, "r") as f:
                return yaml.safe_load(f)
        except Exception:
            return None

    def _write_compose_file(self, compose_file: Path, content: dict[str, Any]) -> None:
        """Write a compose file (blocking, run in thread)."""
        with open(compose_file, "w") as f:
            yaml.dump(content, f, default_flow_style=False)

    def _read_config_file(self, config_file: Path) -> dict[str, Any] | None:
        """Read app configuration file (blocking, run in thread)."""
        try:
            with open(config_file, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return None

    def _write_config_file(self, config_file: Path, config: dict[str, Any]) -> None:
        """Write app configuration file (blocking, run in thread)."""
        with open(config_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False)

    def _write_env_file(
        self, env_file: Path, app_def: AppDefinition, config: dict[str, Any]
    ) -> None:
        """Write .env file for docker-compose (blocking, run in thread)."""
        env_vars = []
        for env in app_def.environment:
            # Get value from config or use default
            key = f"env_{env.name}"
            value = config.get(key, env.default)
            if value:
                env_vars.append(f"{env.name}={value}")

        if env_vars:
            with open(env_file, "w") as f:
                f.write("\n".join(env_vars) + "\n")

    async def update_config(self, app_id: str, config: dict[str, Any]) -> bool:
        """Update configuration for an installed app."""
        app_def = self.catalog.get_app(app_id)
        if not app_def:
            _LOGGER.error("App %s not found in catalog", app_id)
            return False

        stack_dir = self.stacks_path / app_id
        if not stack_dir.exists():
            _LOGGER.error("App %s is not installed", app_id)
            return False

        _LOGGER.info("Updating config for app %s", app_id)

        try:
            # Load existing config and merge with new values
            config_file = stack_dir / "config.yaml"
            existing_config = {}
            if config_file.exists():
                existing_config = await asyncio.to_thread(self._read_config_file, config_file) or {}

            # Merge configs (new values override existing)
            merged_config = {**existing_config, **config}

            # Save updated config
            await asyncio.to_thread(self._write_config_file, config_file, merged_config)

            # Regenerate docker-compose.yml
            compose_content = self._generate_compose(app_def, merged_config)
            compose_file = stack_dir / "docker-compose.yml"
            await asyncio.to_thread(self._write_compose_file, compose_file, compose_content)

            _LOGGER.info("Config updated for app %s, restart required", app_id)
            await self.async_refresh()
            return True

        except Exception as err:
            _LOGGER.error("Error updating config for %s: %s", app_id, err)
            return False

    async def get_app_config(self, app_id: str) -> dict[str, Any] | None:
        """Get current configuration for an installed app."""
        stack_dir = self.stacks_path / app_id
        config_file = stack_dir / "config.yaml"

        if not config_file.exists():
            return {}

        try:
            return await asyncio.to_thread(self._read_config_file, config_file)
        except Exception:
            return None
