"""Sensor platform for my-PV."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


@dataclass(frozen=True, kw_only=True)
class MyPvSensorDescription(SensorEntityDescription):
    """Describe my-PV sensor."""
    value_key: str


SENSORS: tuple[MyPvSensorDescription, ...] = (
    MyPvSensorDescription(
        key="power_nominal",
        name="Power nominal",
        native_unit_of_measurement=UnitOfPower.WATT,
        value_key="power_nominal",
    ),
    MyPvSensorDescription(
        key="power_max",
        name="Power max",
        native_unit_of_measurement=UnitOfPower.WATT,
        value_key="power_max",
    ),
    MyPvSensorDescription(
        key="power_actual",
        name="Power actual",
        native_unit_of_measurement=UnitOfPower.WATT,
        value_key="power",
    ),
    MyPvSensorDescription(
        key="ctrlstate",
        name="Control state",
        value_key="ctrlstate",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data["coordinator"]
    async_add_entities(
        MyPvSensor(coordinator, entry, description) for description in SENSORS
    )


class MyPvSensor(CoordinatorEntity, SensorEntity):
    """Representation of a my-PV sensor."""

    entity_description: MyPvSensorDescription
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry, description: MyPvSensorDescription):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.unique_id)},
            "name": f"mypv_cloudapi {entry.title}",
            "manufacturer": "mypv_cloudapi",
            "model": "Cloud API device",
        }

    @property
    def native_value(self):
        return self.coordinator.data.get(self.entity_description.value_key)