"""Support for the SickGear service."""
from .sickapi import SickApi, SickApiException
from datetime import date, datetime
from dataclasses import dataclass
from typing import TypedDict

from homeassistant.const import CONF_API_KEY, CONF_URL
from homeassistant.core import HomeAssistant

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import EntityDescription

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
    SensorEntity,
)

from .const import LOGGER


async def get_client(hass: HomeAssistant, data):
    """Get SickGear client."""
    api_key = data[CONF_API_KEY]
    url = data[CONF_URL]

    sickgear = SickApi(
        url,
        api_key,
        session=async_get_clientsession(hass, False),
    )
    try:
        await sickgear.check_available()
    except SickApiException as exception:
        LOGGER.error("Connection to SickGear API failed: %s", exception.message)
        return False

    return sickgear


@dataclass
class SickGearEntityDescription(EntityDescription):
    """A class that describes sensor entities."""

    device_class: SensorDeviceClass | None = None
    last_reset: datetime | None = None
    native_unit_of_measurement: str | None = None
    options: list[str] | None = None
    state_class: SensorStateClass | str | None = None
    suggested_display_precision: int | None = None
    suggested_unit_of_measurement: str | None = None
    unit_of_measurement: None = None  # Type override, use native_unit_of_measurement
    category: str | None = None


class Episode(TypedDict, total=True):
    """Dict of Episode Details."""

    show_name: str | None
    show_link: str | None
    episode_number: str | None
    episode_name: str | None
    episode_plot: str | None
    episode_airdate: datetime | None
    episode_network: str | None


class Show(TypedDict, total=True):
    """Dict of Shows and their details."""

    show_name: str | None
    network: str | None
    start_date: date | None


class RootDrive(TypedDict, total=True):
    """Dict of Root Disk details."""

    is_valid: bool | None
    free_space: str | None


class SickGearSensorEntity(SensorEntity):
    """Base class for sensor entities."""

    entity_description: SickGearEntityDescription
    _attr_show = list[Show] | None
    _attr_episode = list[Episode] | None

    def __init__(self, sensor: SensorEntity) -> None:
        """Initialize."""
        super().__init__(sensor)


class SickException(Exception):
    """SickGear Exceptions."""

    def __init__(self, message, mode=None) -> None:
        """Initiate Exception."""
        self.message = message
        self.mode = mode

    def __str__(self):
        """Set Exception Value."""
        if self.mode is not None:
            msg_format = "{}: calling api endpoint '{}'"
        else:
            msg_format = "{}"
        return msg_format.format(
            self.message, self.mode if self.mode is not None else ""
        )
