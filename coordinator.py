"""Data coordinator for my-PV."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MyPvApiAuthError, MyPvApiClient, MyPvApiError
from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class MyPvDataUpdateCoordinator(DataUpdateCoordinator[dict]):
    """Coordinate my-PV data updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: MyPvApiClient,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="mypv_cloudapi",
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.api = api

    async def _async_update_data(self) -> dict:
        try:
            return await self.api.get_data()
        except MyPvApiAuthError as err:
            raise UpdateFailed(f"Authentication error: {err}") from err
        except MyPvApiError as err:
            raise UpdateFailed(f"API error: {err}") from err