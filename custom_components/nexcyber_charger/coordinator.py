"""DataUpdateCoordinator — polls the NexCyber charger's confirmed DPs locally."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NexCyberApiError, NexCyberChargerApi
from .const import DOMAIN, SCAN_INTERVAL_SECONDS

_LOGGER = logging.getLogger(__name__)


class NexCyberCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls the charger over the local network on a fixed interval."""

    def __init__(self, hass: HomeAssistant, api: NexCyberChargerApi, device_id: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{device_id}",
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
        )
        self.api = api
        self.device_id = device_id

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.hass.async_add_executor_job(self.api.get_status)
        except NexCyberApiError as err:
            raise UpdateFailed(f"NexCyber charger error: {err}") from err
        except OSError as err:
            raise UpdateFailed(f"Cannot reach charger: {err}") from err
