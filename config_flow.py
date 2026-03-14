"""Config flow for my-PV."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MyPvApiAuthError, MyPvApiClient, MyPvApiError
from .const import CONF_API_TOKEN, CONF_SERIALNUMBER, DOMAIN


class MyPvConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for my-PV."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            serialnumber = user_input[CONF_SERIALNUMBER]
            api_token = user_input[CONF_API_TOKEN]

            await self.async_set_unique_id(serialnumber)
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            client = MyPvApiClient(session, serialnumber, api_token)

            try:
                data = await client.validate()
            except MyPvApiAuthError:
                errors["base"] = "invalid_auth"
            except MyPvApiError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                title = str(data.get("deviceName") or serialnumber)
                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_SERIALNUMBER: serialnumber,
                        CONF_API_TOKEN: api_token,
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_SERIALNUMBER): str,
                vol.Required(CONF_API_TOKEN): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)