"""The my-PV integration."""

from __future__ import annotations

from typing import Final

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MyPvApiAuthError, MyPvApiClient, MyPvApiError
from .const import (
    ATTR_LEGIONELLA_BOOST_BLOCK,
    ATTR_POWER,
    ATTR_TIME_BOOST_OVERRIDE,
    ATTR_TIME_BOOST_VALUE,
    ATTR_VALID_FOR_MINUTES,
    CONF_API_TOKEN,
    CONF_SERIALNUMBER,
    DOMAIN,
    SERVICE_SET_POWER,
)
from .coordinator import MyPvDataUpdateCoordinator

PLATFORMS: Final[list[Platform]] = [Platform.SENSOR]

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_POWER): vol.All(vol.Coerce(int)),
        vol.Required(ATTR_VALID_FOR_MINUTES): vol.All(vol.Coerce(int)),
        vol.Optional(ATTR_TIME_BOOST_OVERRIDE, default=0): vol.All(vol.Coerce(int)),
        vol.Optional(ATTR_TIME_BOOST_VALUE, default=0): vol.All(vol.Coerce(int)),
        vol.Optional(ATTR_LEGIONELLA_BOOST_BLOCK, default=1): vol.All(vol.Coerce(int)),
        vol.Optional("entry_id"): str,
    }
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration domain."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up my-PV from a config entry."""
    session = async_get_clientsession(hass)
    api = MyPvApiClient(
        session=session,
        serialnumber=entry.data[CONF_SERIALNUMBER],
        api_token=entry.data[CONF_API_TOKEN],
    )

    try:
        compatible = await api.is_firmware_compatible()
        if not compatible:
            raise ConfigEntryNotReady("Firmware not compatible")
    except MyPvApiAuthError as err:
        raise ConfigEntryNotReady(f"Authentication failed: {err}") from err
    except MyPvApiError as err:
        raise ConfigEntryNotReady(f"API unavailable: {err}") from err

    coordinator = MyPvDataUpdateCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = {
        "api": api,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    if not hass.services.has_service(DOMAIN, SERVICE_SET_POWER):

        async def async_handle_set_power(call: ServiceCall) -> None:
            target_entry_id = call.data.get("entry_id")
            power = call.data[ATTR_POWER]
            valid_for_minutes = call.data[ATTR_VALID_FOR_MINUTES]
            time_boost_override = call.data[ATTR_TIME_BOOST_OVERRIDE]
            time_boost_value = call.data[ATTR_TIME_BOOST_VALUE]
            legionella_boost_block = call.data[ATTR_LEGIONELLA_BOOST_BLOCK]

            if target_entry_id:
                runtime = next(
                    (
                        e.runtime_data
                        for e in hass.config_entries.async_entries(DOMAIN)
                        if e.entry_id == target_entry_id
                    ),
                    None,
                )
            else:
                entries = hass.config_entries.async_entries(DOMAIN)
                if len(entries) != 1:
                    raise HomeAssistantError(
                        "entry_id is required when more than one my-PV device is configured"
                    )
                runtime = entries[0].runtime_data

            if runtime is None:
                raise HomeAssistantError("Target device not found")

            api_client: MyPvApiClient = runtime["api"]
            coordinator: MyPvDataUpdateCoordinator = runtime["coordinator"]

            await api_client.set_power(
                power=power,
                valid_for_minutes=valid_for_minutes,
                time_boost_override=time_boost_override,
                time_boost_value=time_boost_value,
                legionella_boost_block=legionella_boost_block,
            )

            await coordinator.async_request_refresh()

        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_POWER,
            async_handle_set_power,
            schema=SERVICE_SCHEMA,
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)