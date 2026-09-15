"""Config flow for the NexCyber EV Charger — local network setup, no cloud."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .api import NexCyberApiError, NexCyberChargerApi
from .const import (
    CONF_DEVICE_ID,
    CONF_HOST,
    CONF_LOCAL_KEY,
    CONF_PROTOCOL_VERSION,
    DEFAULT_PROTOCOL_VERSION,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_DEVICE_ID): str,
        vol.Required(CONF_LOCAL_KEY): str,
        vol.Optional(CONF_PROTOCOL_VERSION, default=DEFAULT_PROTOCOL_VERSION): vol.Coerce(float),
    }
)


def _validate(data: dict[str, Any]) -> None:
    """Connect and pull one status snapshot — raises on any failure.

    Runs in an executor thread; must not touch the event loop.
    """
    api = NexCyberChargerApi(
        data[CONF_DEVICE_ID], data[CONF_LOCAL_KEY], data[CONF_HOST], data[CONF_PROTOCOL_VERSION]
    )
    try:
        api.get_status()
    finally:
        api.close()


class NexCyberConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the NexCyber EV Charger."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
            self._abort_if_unique_id_configured()

            hass: HomeAssistant = self.hass
            try:
                await hass.async_add_executor_job(_validate, user_input)
            except NexCyberApiError as err:
                _LOGGER.error("Validation failed: %s", err)
                errors["base"] = "cannot_connect"
            except OSError as err:
                _LOGGER.error("Cannot reach charger at %s: %s", user_input[CONF_HOST], err)
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title="NexCyber EV Charger", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
