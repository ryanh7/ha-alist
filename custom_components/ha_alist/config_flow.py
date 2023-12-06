from __future__ import annotations
import logging
import hashlib

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_NAME, CONF_HOST, CONF_USERNAME, CONF_PASSWORD

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class AlistFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}

        if user_input is not None:
            user_input[CONF_PASSWORD] = hashlib.sha256(f"{user_input[CONF_PASSWORD]}-https://github.com/alist-org/alist".encode("utf-8")).hexdigest()
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                    {
                        vol.Required(CONF_NAME, default="Alist"): str,
                        vol.Required(CONF_HOST, default="http://localhost:80"): str,
                        vol.Required(CONF_USERNAME): str,
                        vol.Required(CONF_PASSWORD): str,
                    }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.config = dict(config_entry.data)

    async def async_step_init(self, user_input=None):
        errors = {}

        if user_input is not None:
            if self.config.get(CONF_PASSWORD) != user_input[CONF_PASSWORD]:
                user_input[CONF_PASSWORD] = hashlib.sha256(f"{user_input[CONF_PASSWORD]}-https://github.com/alist-org/alist".encode("utf-8")).hexdigest()
            self.config.update(user_input)
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=self.config
            )
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data=self.config)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                    {
                        vol.Required(CONF_NAME, default=self.config.get(CONF_NAME)): str,
                        vol.Required(CONF_HOST, default=self.config.get(CONF_HOST)): str,
                        vol.Required(CONF_USERNAME, default=self.config.get(CONF_USERNAME)): str,
                        vol.Required(CONF_PASSWORD, default=self.config.get(CONF_PASSWORD)): str,
                    }
            ),
            errors=errors,
        )
