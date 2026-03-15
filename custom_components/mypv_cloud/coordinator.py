"""Data coordinator for my-PV Cloud."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MyPvApiAuthError, MyPvApiClient, MyPvApiError
from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class MyPvDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate my-PV cloud data updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: MyPvApiClient,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="mypv_cloud",
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            current_data = await self.api.get_data()
            solar_forecast = await self.api.get_solar_forecast()

            return {
                "data": current_data,
                "solar_forecast": solar_forecast,
            }

        except MyPvApiAuthError as err:
            raise UpdateFailed(f"Authentication error: {err}") from err
        except MyPvApiError as err:
            raise UpdateFailed(f"API error: {err}") from err