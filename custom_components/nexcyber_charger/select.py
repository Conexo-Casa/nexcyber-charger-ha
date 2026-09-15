"""Select platform for the NexCyber EV Charger — charge mode."""

from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import NexCyberApiError, NexCyberChargerApi
from .const import DOMAIN, DP_WORK_MODE, WORK_MODE_OPTIONS
from .coordinator import NexCyberCoordinator
from .entity import NexCyberEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NexCyberWorkMode(data["coordinator"], data["api"])])


class NexCyberWorkMode(NexCyberEntity, SelectEntity):
    """Charge mode: charge_now / charge_pct / charge_energy / charge_schedule."""

    _attr_name = "Charge Mode"
    _attr_icon = "mdi:ev-plug-type1"
    _attr_options = WORK_MODE_OPTIONS

    def __init__(self, coordinator: NexCyberCoordinator, api: NexCyberChargerApi) -> None:
        super().__init__(coordinator, "work_mode")
        self._api = api

    @property
    def current_option(self) -> str | None:
        return self.coordinator.data.get(str(DP_WORK_MODE))

    async def async_select_option(self, option: str) -> None:
        try:
            await self.hass.async_add_executor_job(self._api.set_dp, DP_WORK_MODE, option)
        except NexCyberApiError as err:
            _LOGGER.error("Failed to set charge mode: %s", err)
            return
        await self.coordinator.async_request_refresh()
