"""SickGear Binary Sensors."""
from __future__ import annotations


from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN
from .const import (
    # LOGGER,
    DEFAULT_NAME,
    KEY_API_DATA,
    KEY_NAME,
    BACKLOG_PAUSED,
    BACKLOG_RUNNING,
)


BINARY_SENSORS = (
    BinarySensorEntityDescription(
        key=BACKLOG_PAUSED,
        name="Backlog Enabled",
        icon="mdi:television-play",
    ),
    BinarySensorEntityDescription(
        key=BACKLOG_RUNNING,
        name="Backlog Running",
        icon="mdi:television-play",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up a SickGear sensor entry."""

    entry_id = config_entry.entry_id

    sick_api_data = hass.data[DOMAIN][entry_id][KEY_API_DATA]
    client_name = hass.data[DOMAIN][entry_id][KEY_NAME]

    async_add_entities(
        [
            SickGearBinarySensor(sick_api_data, client_name, sensor, entry_id)
            for sensor in BINARY_SENSORS
        ]
    )


class SickGearBinarySensor(BinarySensorEntity):
    """Representation of a SickGear sensor."""

    entity_description: BinarySensorEntityDescription
    _attr_should_poll = True

    def __init__(
        self,
        sick_api_data,
        client_name,
        description: BinarySensorEntityDescription,
        entry_id,
    ) -> None:
        """Initialize the sensor."""

        self._attr_unique_id = f"{entry_id}_{description.key}"
        self.entity_description = description
        self._sickgear_api = sick_api_data
        self._attr_name = f"{client_name} {description.name}"
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, entry_id)},
            name=DEFAULT_NAME,
        )

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        setting = self._sickgear_api.get_schedule_setting(self.entity_description.key)

        on_values = {
            "backlog_is_paused": 0,
            "backlog_is_running": 1,
        }

        is_enabled = on_values[self.entity_description.key] == setting
        return is_enabled
