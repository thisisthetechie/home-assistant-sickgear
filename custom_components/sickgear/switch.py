"""Switch platform for sickgear."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.switch import (
    SwitchEntity,
    SwitchEntityDescription,
)
from . import DOMAIN
from .sickgear import SickException
from .const import (
    # LOGGER,
    KEY_API_DATA,
    KEY_NAME,
    DEFAULT_NAME,
    BACKLOG_PAUSED,
)

SWITCHES = (
    SwitchEntityDescription(
        key=BACKLOG_PAUSED,
        name="Backlog Enabled",
        icon="mdi:television-play",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up a Switch."""
    entry_id = config_entry.entry_id
    sick_api_data = hass.data[DOMAIN][entry_id][KEY_API_DATA]
    client_name = hass.data[DOMAIN][entry_id][KEY_NAME]
    async_add_entities(
        [
            SickGearSwitch(
                sick_api_data,
                client_name,
                switch,
                entry_id,
            )
            for switch in SWITCHES
        ],
        True,
    )


class SickGearSwitch(SwitchEntity):
    """SickGear switch class."""

    def __init__(
        self,
        sick_api_data,
        client_name,
        description: SwitchEntityDescription,
        entry_id,
    ) -> None:
        """Initialize the switch class."""
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self.entity_description = description
        self._sickgear_api = sick_api_data
        self._attr_name = f"{client_name} {description.name}"
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, entry_id)},
            name=DEFAULT_NAME,
            manufacturer="SickGear",
            model="SickGear",
        )

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        try:
            setting = self._sickgear_api.get_schedule_setting(
                self.entity_description.key
            )
            on_values = {
                BACKLOG_PAUSED: 0,
            }
            return on_values[self.entity_description.key] == setting
        except SickException as exception:
            raise PlatformNotReady() from exception

    async def async_turn_on(self, **_: any) -> None:
        """Turn on the switch."""
        await self._sickgear_api.async_backlog_enable()
        await self._sickgear_api.sick_api.refresh_data()

    async def async_turn_off(self, **_: any) -> None:
        """Turn off the switch."""
        await self._sickgear_api.async_backlog_disable()
        await self._sickgear_api.sick_api.refresh_data()
