"""Switch platform for the NexCyber EV Charger — charging on/off.

Charging on/off is a genuinely stateful, idempotent toggle (unlike a one-shot
"start session" action), so a switch is the right entity — pair it with an HA
Schedule Helper or automation for timed charging rather than the charger's own
undocumented `local_timer` datapoint.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import NexCyberApiError, NexCyberChargerApi
from .const import DOMAIN, DP_SWITCH
from .coordinator import NexCyberCoordinator
from .entity import NexCyberEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NexCyberChargeSwitch(data["coordinator"], data["api"])])


class NexCyberChargeSwitch(NexCyberEntity, SwitchEntity):
    """Turn charging on/off."""

    _attr_name = "Charging"
    _attr_device_class = SwitchDeviceClass.OUTLET
    _attr_icon = "mdi:ev-station"

    def __init__(self, coordinator: NexCyberCoordinator, api: NexCyberChargerApi) -> None:
        super().__init__(coordinator, "switch")
        self._api = api

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.get(str(DP_SWITCH))

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._async_set(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_set(False)

    async def _async_set(self, value: bool) -> None:
        try:
            await self.hass.async_add_executor_job(self._api.set_dp, DP_SWITCH, value)
        except NexCyberApiError as err:
            _LOGGER.error("Failed to set charger switch: %s", err)
            return
        await self.coordinator.async_request_refresh()
