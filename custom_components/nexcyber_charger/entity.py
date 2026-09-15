"""Base entity for the NexCyber EV Charger integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NexCyberCoordinator


class NexCyberEntity(CoordinatorEntity[NexCyberCoordinator]):
    """Common base: ties every entity to the charger's HA device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: NexCyberCoordinator, key: str) -> None:
        """Set the unique id and device metadata."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.device_id)},
            manufacturer="NexCyber",
            model="48A Level 2 EV Charger",
            name="NexCyber EV Charger",
        )
