# custom_components/mypv_cloud/config_flow.py
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MyPvApiClient, MyPvApiError
from .const import CONF_API_TOKEN, CONF_SERIALNUMBER, DOMAIN


class MyPvCloudConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_SERIALNUMBER])
            self._abort_if_unique_id_configured()

            try:
                session = async_get_clientsession(self.hass)
                api = MyPvApiClient(
                    session=session,
                    serialnumber=user_input[CONF_SERIALNUMBER],
                    api_token=user_input[CONF_API_TOKEN],
                )
                await api.validate()
            except MyPvApiError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_SERIALNUMBER],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SERIALNUMBER): str,
                    vol.Required(CONF_API_TOKEN): str,
                }
            ),
            errors=errors,
        )