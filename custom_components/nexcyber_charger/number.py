"""Number platform for the NexCyber EV Charger — charge current limit."""

from __future__ import annotations

import logging

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricCurrent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import NexCyberApiError, NexCyberChargerApi
from .const import CHARGE_CUR_MAX, CHARGE_CUR_MIN, DOMAIN, DP_CHARGE_CUR_SET
from .coordinator import NexCyberCoordinator
from .entity import NexCyberEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NexCyberCurrentLimit(data["coordinator"], data["api"])])


class NexCyberCurrentLimit(NexCyberEntity, NumberEntity):
    """Charging current limit, 8-48A (`charge_cur_set`)."""

    _attr_name = "Charge Current Limit"
    _attr_icon = "mdi:current-ac"
    _attr_device_class = NumberDeviceClass.CURRENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_native_min_value = CHARGE_CUR_MIN
    _attr_native_max_value = CHARGE_CUR_MAX
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator: NexCyberCoordinator, api: NexCyberChargerApi) -> None:
        super().__init__(coordinator, "charge_cur_set")
        self._api = api

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.get(str(DP_CHARGE_CUR_SET))

    async def async_set_native_value(self, value: float) -> None:
        try:
            await self.hass.async_add_executor_job(
                self._api.set_dp, DP_CHARGE_CUR_SET, int(value)
            )
        except NexCyberApiError as err:
            _LOGGER.error("Failed to set charge current limit: %s", err)
            return
        await self.coordinator.async_request_refresh()
