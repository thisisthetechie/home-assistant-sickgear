"""Adds config flow for SickGear Integration."""
from __future__ import annotations

from typing import Any


import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from homeassistant.const import (
    CONF_API_KEY,
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    CONF_SSL,
    CONF_URL,
)


from .sickgear import get_client
from .const import DOMAIN, DEFAULT_NAME

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL): str,
        vol.Required(CONF_API_KEY): str,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
    }
)

class SickGearConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for SickGear Integration."""

    VERSION = 1

    async def _async_validate_input(self, user_input):
        """Validate the user input allows us to connect."""
        errors = {}
        sick_api = await get_client(self.hass, user_input)
        if not sick_api:
            errors["base"] = "cannot_connect"

        return errors

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""

        errors = {}
        if user_input is not None:
            errors = await self._async_validate_input(user_input)

            if not errors:
                return self.async_create_entry(
                    title=user_input[CONF_API_KEY][:12], data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=USER_SCHEMA,
            errors=errors if errors else None,
            description_placeholders={
                CONF_API_KEY: "CONF_API_KEY",
                CONF_NAME: "CONF_NAME",
                CONF_URL: "CONF_URL",
            },
        )

    async def async_step_import(self, import_data):
        """Import SickGear config from configuration.yaml."""
        protocol = "https://" if import_data[CONF_SSL] else "http://"
        import_data[
            CONF_URL
        ] = f"{protocol}{import_data[CONF_HOST]}:{import_data[CONF_PORT]}/api/{import_data[CONF_API_KEY]}"
        return await self.async_step_user(import_data)
