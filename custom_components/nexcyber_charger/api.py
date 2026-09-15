"""Local Tuya API wrapper for the NexCyber EV Charger.

tinytuya is synchronous — every method here does blocking socket I/O and must
only be called from a Home Assistant executor thread
(``hass.async_add_executor_job``), never awaited directly.
"""

from __future__ import annotations

import logging
from typing import Any

import tinytuya

_LOGGER = logging.getLogger(__name__)


class NexCyberApiError(Exception):
    """Raised when a call to the charger fails or returns something unexpected."""


class NexCyberChargerApi:
    """Thin synchronous wrapper around ``tinytuya.Device`` for one charger."""

    def __init__(self, device_id: str, local_key: str, host: str, version: float) -> None:
        self._device = tinytuya.Device(device_id, host, local_key, version=version)
        self._device.set_socketPersistent(True)

    def get_status(self) -> dict[str, Any]:
        """Return the raw ``dps`` dict (numeric-dpId string keys)."""
        result = self._device.status()
        if not isinstance(result, dict) or "dps" not in result:
            raise NexCyberApiError(f"Unexpected response from charger: {result}")
        return result["dps"]

    def set_dp(self, dp: int, value: Any) -> None:
        """Write a single datapoint."""
        result = self._device.set_value(dp, value, nowait=False)
        if isinstance(result, dict) and result.get("Error"):
            raise NexCyberApiError(result["Error"])

    def close(self) -> None:
        """Best-effort socket cleanup on unload."""
        try:
            self._device.close()
        except Exception:
            _LOGGER.debug("Error closing charger connection", exc_info=True)
