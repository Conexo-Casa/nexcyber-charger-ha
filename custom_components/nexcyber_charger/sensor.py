"""Sensor platform for the NexCyber EV Charger.

Each sensor maps to one confirmed datapoint and extracts its value with a
``value_fn`` that applies that DP's scale conversion (see const.py — scale
divisors and the note on why the raw/undocumented DPs are left unmapped).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    EntityCategory,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import (
    CONNECTION_STATE_OPTIONS,
    DOMAIN,
    DP_CHARGE_ENERGY_ONCE,
    DP_CONNECTION_STATE,
    DP_FORWARD_ENERGY_TOTAL,
    DP_POWER_TOTAL,
    DP_TEMP_CURRENT,
    DP_WORK_STATE,
    SCALE_CHARGE_ENERGY_ONCE,
    SCALE_FORWARD_ENERGY_TOTAL,
    SCALE_POWER_TOTAL,
    WORK_STATE_OPTIONS,
)
from .coordinator import NexCyberCoordinator
from .entity import NexCyberEntity


@dataclass(frozen=True, kw_only=True)
class NexCyberSensorDescription(SensorEntityDescription):
    """Sensor description with a source dpId and a raw-value extractor."""

    dp: int
    value_fn: Callable[[Any], StateType]


SENSORS: tuple[NexCyberSensorDescription, ...] = (
    NexCyberSensorDescription(
        key="power_total",
        translation_key="power_total",
        dp=DP_POWER_TOTAL,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda raw: raw / SCALE_POWER_TOTAL,
    ),
    NexCyberSensorDescription(
        key="forward_energy_total",
        translation_key="forward_energy_total",
        dp=DP_FORWARD_ENERGY_TOTAL,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda raw: raw / SCALE_FORWARD_ENERGY_TOTAL,
    ),
    NexCyberSensorDescription(
        key="charge_energy_once",
        translation_key="charge_energy_once",
        dp=DP_CHARGE_ENERGY_ONCE,
        icon="mdi:ev-station",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda raw: raw / SCALE_CHARGE_ENERGY_ONCE,
    ),
    NexCyberSensorDescription(
        key="temp_current",
        translation_key="temp_current",
        dp=DP_TEMP_CURRENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda raw: raw,
    ),
    NexCyberSensorDescription(
        key="work_state",
        translation_key="work_state",
        dp=DP_WORK_STATE,
        device_class=SensorDeviceClass.ENUM,
        options=WORK_STATE_OPTIONS,
        icon="mdi:ev-station",
        value_fn=lambda raw: raw,
    ),
    NexCyberSensorDescription(
        key="connection_state",
        translation_key="connection_state",
        dp=DP_CONNECTION_STATE,
        device_class=SensorDeviceClass.ENUM,
        options=CONNECTION_STATE_OPTIONS,
        icon="mdi:ev-plug-type1",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda raw: raw,
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NexCyber charger sensors."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: NexCyberCoordinator = data["coordinator"]
    async_add_entities(NexCyberSensor(coordinator, description) for description in SENSORS)


class NexCyberSensor(NexCyberEntity, SensorEntity):
    """A single NexCyber-charger-derived sensor."""

    entity_description: NexCyberSensorDescription

    def __init__(
        self, coordinator: NexCyberCoordinator, description: NexCyberSensorDescription
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def available(self) -> bool:
        return (
            super().available
            and str(self.entity_description.dp) in self.coordinator.data
        )

    @property
    def native_value(self) -> StateType:
        raw = self.coordinator.data.get(str(self.entity_description.dp))
        if raw is None:
            return None
        return self.entity_description.value_fn(raw)
