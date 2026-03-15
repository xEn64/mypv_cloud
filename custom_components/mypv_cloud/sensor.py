"""Sensor platform for my-PV Cloud."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from datetime import datetime, timedelta
from .const import DOMAIN


@dataclass(frozen=True, kw_only=True)
class MyPvSensorDescription(SensorEntityDescription):
    """Describe my-PV sensor."""
    value_key: str
    source: str = "data"


SENSORS: tuple[MyPvSensorDescription, ...] = (
    MyPvSensorDescription(
        key="power_nominal",
        name="Power nominal",
        native_unit_of_measurement=UnitOfPower.WATT,
        value_key="power_nominal",
        source="data",
    ),
    MyPvSensorDescription(
        key="power_max",
        name="Power max",
        native_unit_of_measurement=UnitOfPower.WATT,
        value_key="power_max",
        source="data",
    ),
    MyPvSensorDescription(
        key="power_actual",
        name="Power actual",
        native_unit_of_measurement=UnitOfPower.WATT,
        value_key="power",
        source="data",
    ),
    MyPvSensorDescription(
        key="ctrlstate",
        name="Control state",
        value_key="ctrlstate",
        source="data",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data["coordinator"]

    entities: list[SensorEntity] = [
        MyPvSensor(coordinator, entry, description) for description in SENSORS
    ]

    entities.extend(
        [
            MyPvForecastTodaySensor(coordinator, entry),
            MyPvForecastTomorrowSensor(coordinator, entry),
            MyPvForecastDayAfterTomorrowSensor(coordinator, entry),
        ]
    )

    async_add_entities(entities)


class MyPvBaseSensor(CoordinatorEntity, SensorEntity):
    """Base sensor for my-PV Cloud."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry, unique_suffix: str, name: str):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{unique_suffix}"
        self._attr_name = name
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.unique_id)},
            "name": f"my-PV Cloud {entry.title}",
            "manufacturer": "my-PV",
            "model": "Cloud API",
        }


class MyPvSensor(MyPvBaseSensor):
    """Representation of a standard my-PV sensor."""

    entity_description: MyPvSensorDescription

    def __init__(self, coordinator, entry: ConfigEntry, description: MyPvSensorDescription):
        super().__init__(coordinator, entry, description.key, description.name)
        self.entity_description = description

    @property
    def native_value(self):
        root = self.coordinator.data.get(self.entity_description.source, {})
        if not isinstance(root, dict):
            return None
        return root.get(self.entity_description.value_key)


class MyPvForecastBaseSensor(MyPvBaseSensor):
    """Base class for day forecast sensors."""

    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    _attr_icon = "mdi:weather-sunny"

    def _get_day_value(self, offset_days: int):
        forecast = self.coordinator.data.get("solar_forecast", {})
        if not isinstance(forecast, dict):
            return None

        watt_hours_day = forecast.get("watt_hours_day", {})
        if not isinstance(watt_hours_day, dict):
            return None

        target_str = (datetime.now().date() + timedelta(days=offset_days)).isoformat()
        return watt_hours_day.get(target_str)

class MyPvForecastTodaySensor(MyPvForecastBaseSensor):
    """Forecast for today."""

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry, "pv_forecast_today_wh", "PV forecast today")

    @property
    def native_value(self):
        return self._get_day_value(0)


class MyPvForecastTomorrowSensor(MyPvForecastBaseSensor):
    """Forecast for tomorrow."""

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry, "pv_forecast_tomorrow_wh", "PV forecast tomorrow")

    @property
    def native_value(self):
        return self._get_day_value(1)


class MyPvForecastDayAfterTomorrowSensor(MyPvForecastBaseSensor):
    """Forecast for day after tomorrow."""

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry, "pv_forecast_day_after_tomorrow_wh", "PV forecast day after tomorrow")

    @property
    def native_value(self):
        return self._get_day_value(2)