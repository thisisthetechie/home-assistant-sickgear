"""Support for monitoring a SickGear client."""
from __future__ import annotations

from collections.abc import Callable

from .sickapi import SickApiException
import voluptuous as vol

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import (
    CONF_API_KEY,
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    CONF_SENSORS,
    CONF_SSL,
    Platform,
)
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.device_registry import async_get
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.entity_registry import RegistryEntry, async_migrate_entries
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.typing import ConfigType

from .const import (
    LOGGER,
    ATTR_API_KEY,
    DEFAULT_HOST,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SSL,
    DOMAIN,
    KEY_API,
    KEY_API_DATA,
    KEY_NAME,
    SIGNAL_SICKGEAR_UPDATED,
    UPDATE_INTERVAL,
)
from .sickgear import get_client

PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]

SERVICE_BASE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_API_KEY): cv.string,
    }
)


CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            vol.All(
                cv.deprecated(CONF_HOST),
                cv.deprecated(CONF_PORT),
                cv.deprecated(CONF_SENSORS),
                cv.deprecated(CONF_SSL),
                {
                    vol.Required(CONF_API_KEY): str,
                    vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                    vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                    vol.Optional(CONF_SSL, default=DEFAULT_SSL): cv.boolean,
                },
            )
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the SickGear component."""
    hass.data.setdefault(DOMAIN, {})

    if hass.config_entries.async_entries(DOMAIN):
        return True

    if DOMAIN in config:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": SOURCE_IMPORT},
                data=config[DOMAIN],
            )
        )

    return True


@callback
def async_get_entry_id_for_service_call(hass: HomeAssistant, call: ServiceCall) -> str:
    """Get the entry ID related to a service call (by device ID)."""
    call_data_api_key = call.data[ATTR_API_KEY]

    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.data[ATTR_API_KEY] == call_data_api_key:
            return entry.entry_id

    raise ValueError(f"No api for API key: {call_data_api_key}")


def update_device_identifiers(hass: HomeAssistant, entry: ConfigEntry):
    """Update device identifiers to new identifiers."""
    device_registry = async_get(hass)
    device_entry = device_registry.async_get_device({(DOMAIN, DOMAIN)})
    if device_entry and entry.entry_id in device_entry.config_entries:
        new_identifiers = {(DOMAIN, entry.entry_id)}
        LOGGER.debug(
            "Updating device id <%s> with new identifiers <%s>",
            device_entry.id,
            new_identifiers,
        )
        device_registry.async_update_device(
            device_entry.id, new_identifiers=new_identifiers
        )


async def migrate_unique_id(hass: HomeAssistant, entry: ConfigEntry):
    """Migrate entities to new unique ids (with entry_id)."""

    @callback
    def async_migrate_callback(entity_entry: RegistryEntry) -> dict | None:
        """Define a callback to migrate appropriate SickGearSensor entities to new unique IDs.

        Old: description.key
        New: {entry_id}_description.key
        """
        entry_id = entity_entry.config_entry_id
        if entry_id is None:
            return None
        if entity_entry.unique_id.startswith(entry_id):
            return None

        new_unique_id = f"{entry_id}_{entity_entry.unique_id}"

        LOGGER.debug(
            "Migrating entity %s from old unique ID '%s' to new unique ID '%s'",
            entity_entry.entity_id,
            entity_entry.unique_id,
            new_unique_id,
        )

        return {"new_unique_id": new_unique_id}

    await async_migrate_entries(hass, entry.entry_id, async_migrate_callback)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the SickGear Component."""

    sick_api = await get_client(hass, entry.data)
    if not sick_api:
        raise ConfigEntryNotReady

    sick_api_data = SickGearApiData(sick_api)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        KEY_API: sick_api,
        KEY_API_DATA: sick_api_data,
        KEY_NAME: entry.data[CONF_NAME],
    }

    await migrate_unique_id(hass, entry)
    update_device_identifiers(hass, entry)

    @callback
    def extract_api(func: Callable) -> Callable:
        """Define a decorator to get the correct api for a service call."""

        async def wrapper(call: ServiceCall) -> None:
            """Wrap the service function."""
            entry_id = async_get_entry_id_for_service_call(hass, call)
            api_data = hass.data[DOMAIN][entry_id][KEY_API_DATA]

            try:
                await func(call, api_data)
            except Exception as err:
                raise HomeAssistantError(
                    f"Error while executing {func.__name__}: {err}"
                ) from err

        return wrapper

    @extract_api
    async def async_pause_queue(call: ServiceCall, api: SickGearApiData) -> None:
        await api.async_pause_queue()

    @extract_api
    async def async_resume_queue(call: ServiceCall, api: SickGearApiData) -> None:
        await api.async_resume_queue()

    async def async_update_sickgear(now):
        """Refresh SickGear queue data."""
        try:
            await sick_api.refresh_data()
            async_dispatcher_send(hass, SIGNAL_SICKGEAR_UPDATED, None)
        except SickApiException as err:
            LOGGER.error(err)

    async_track_time_interval(hass, async_update_sickgear, UPDATE_INTERVAL)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a SickGear config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class SickGearApiData:
    """Class for storing/refreshing SickGear api queue data."""

    def __init__(self, sick_api) -> None:
        """Initialize component."""
        self.sick_api = sick_api

    async def async_pause_queue(self):
        """Pause SickGear queue."""

        try:
            return await self.sick_api.pause_queue()
        except SickApiException as err:
            LOGGER.error(err)
            return False

    async def async_resume_queue(self):
        """Resume SickGear queue."""

        try:
            return await self.sick_api.resume_queue()
        except SickApiException as err:
            LOGGER.error(err)
            return False

    def get_show_stat(self, stat):
        """Return the value for the given field from the SickGear queue."""
        return self.sick_api.shows_stats.get(stat)

    def get_schedule_setting(self, setting):
        """Return the value for the given field from the SickGear queue."""
        return self.sick_api.scheduler.get(setting)

    def get_upcoming_shows(self, key):
        """Return the value for the given field from the SickGear queue."""
        return self.sick_api.shows_upcoming.get(key)
