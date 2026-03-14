"""API client for my-PV cloud API."""

from __future__ import annotations

from typing import Any

import aiohttp


class MyPvApiError(Exception):
    """Base API error."""


class MyPvApiAuthError(MyPvApiError):
    """Authentication error."""


class MyPvApiClient:
    """Minimal async client for my-PV."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        serialnumber: str,
        api_token: str,
    ) -> None:
        self._session = session
        self._serialnumber = serialnumber
        self._api_token = api_token

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _url(self, suffix: str) -> str:
        return f"https://api.my-pv.com/api/v1/device/{self._serialnumber}/{suffix}"

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Any:
        if response.status in (401, 403):
            text = await response.text()
            raise MyPvApiAuthError(f"Authentication failed: {response.status} {text}")

        if response.status >= 400:
            text = await response.text()
            raise MyPvApiError(f"API request failed: {response.status} {text}")

        try:
            return await response.json()
        except aiohttp.ContentTypeError as err:
            text = await response.text()
            raise MyPvApiError(f"Invalid JSON response: {text}") from err

    async def is_firmware_compatible(self) -> bool:
        """Check firmware compatibility."""
        async with self._session.get(
            self._url("isFirmwareCompatible"),
            headers=self._headers,
            timeout=aiohttp.ClientTimeout(total=20),
        ) as response:
            data = await self._handle_response(response)

        value = data.get("isFirmwareCompatible")
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() == "true"
        return False

    async def get_data(self) -> dict[str, Any]:
        """Fetch current device data."""
        async with self._session.get(
            self._url("data"),
            headers=self._headers,
            timeout=aiohttp.ClientTimeout(total=20),
        ) as response:
            data = await self._handle_response(response)

        if not isinstance(data, dict):
            raise MyPvApiError("Unexpected payload for /data")
        return data

    async def set_power(
        self,
        power: int,
        valid_for_minutes: int,
        time_boost_override: int = 0,
        time_boost_value: int = 0,
        legionella_boost_block: int = 1,
    ) -> dict[str, Any]:
        """Set power for a given duration."""
        payload = {
            "power": int(power),
            "validForMinutes": int(valid_for_minutes),
            "timeBoostOverride": int(time_boost_override),
            "timeBoostValue": int(time_boost_value),
            "legionellaBoostBlock": int(legionella_boost_block),
        }

        async with self._session.post(
            self._url("power"),
            headers=self._headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=20),
        ) as response:
            data = await self._handle_response(response)

        if not isinstance(data, dict):
            return {"result": data}
        return data

    async def validate(self) -> dict[str, Any]:
        """Validate credentials and basic device access."""
        compatible = await self.is_firmware_compatible()
        if not compatible:
            raise MyPvApiError("Firmware is not compatible for API usage")

        return await self.get_data()