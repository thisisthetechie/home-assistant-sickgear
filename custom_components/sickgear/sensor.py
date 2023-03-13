"""SickGear Sensors."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN, SIGNAL_SICKGEAR_UPDATED
from .const import DEFAULT_NAME, KEY_API_DATA, KEY_NAME
from .sickgear import (
    SickGearEntityDescription,
    SickGearSensorEntity,
    Episode,
    RootDrive,
)

from .const import (
    # LOGGER,
    ATTRIBUTE_KEY,
    SHOW_NAME,
    EPISODE_NAME,
    SEASON_NUMBER,
    EPISODE_NUMBER,
    AIR_DATE,
    NETWORK,
    WEB_ROOT,
    EPISODE_PLOT,
    MISSING_EPISODES,
    DOWNLOADED_EPISODES,
    TOTAL_EPISODES,
    BACKLOG_LAST,
    BACKLOG_NEXT,
    SHOW_ID,
    SHOWS_ACTIVE,
    SHOWS_TOTAL,
    SHOWS_LATER,
    SHOWS_TODAY,
    SHOWS_SOON,
    SHOWS_MISSED,
    DISK_LOCATION,
    DISK_PRIMARY,
    DISK_SPACE,
    DISK_VALID,
)


SENSORS = (
    SickGearEntityDescription(
        key=SHOWS_TOTAL,
        name="Show Count",
        icon="mdi:television",
        category="shows",
    ),
    SickGearEntityDescription(
        key=SHOWS_ACTIVE,
        name="Active Shows",
        icon="mdi:television-shimmer",
        category="shows",
    ),
    SickGearEntityDescription(
        key=DOWNLOADED_EPISODES,
        name="Downloaded Episodes",
        icon="mdi:television",
        category="shows",
    ),
    SickGearEntityDescription(
        key=TOTAL_EPISODES,
        name="Total Episodes",
        icon="mdi:television",
        category="shows",
    ),
    SickGearEntityDescription(
        key=MISSING_EPISODES,
        name="Missing Episodes",
        icon="mdi:television-off",
        category="shows",
    ),
    SickGearEntityDescription(
        key=BACKLOG_LAST,
        name="Last Backlog Run",
        icon="mdi:television-guide",
        category="backlog",
    ),
    SickGearEntityDescription(
        key=BACKLOG_NEXT,
        name="Next Backlog Run",
        icon="mdi:television-guide",
        category="backlog",
    ),
    SickGearEntityDescription(
        key=SHOWS_LATER,
        name="Future Shows",
        icon="mdi:television-guide",
        category="upcoming",
    ),
    SickGearEntityDescription(
        key=SHOWS_SOON,
        name="Airing Soon",
        icon="mdi:television-guide",
        category="upcoming",
    ),
    SickGearEntityDescription(
        key=SHOWS_TODAY,
        name="Airing Today",
        icon="mdi:television-guide",
        category="upcoming",
    ),
    SickGearEntityDescription(
        key=SHOWS_MISSED,
        name="Missed Shows",
        icon="mdi:television-guide",
        category="upcoming",
    ),
    SickGearEntityDescription(
        key="primary_disk",
        name="Default Disk",
        icon="mdi:harddisk",
        category="disks",
    ),
    SickGearEntityDescription(
        key="secondary_disk",
        name="Other Disks",
        icon="mdi:harddisk-plus",
        category="disks",
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
            SickGearSensor(sick_api_data, client_name, sensor, entry_id)
            for sensor in SENSORS
        ]
    )


class SickGearSensor(SickGearSensorEntity):
    """Representation of a SickGear sensor."""

    entity_description: SickGearEntityDescription
    _attr_should_poll = False

    def __init__(
        self,
        sick_api_data,
        client_name,
        description: SickGearEntityDescription,
        entry_id,
    ) -> None:
        """Initialize the sensor."""
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self.entity_description = description
        self._sickgear_api = sick_api_data
        self._attr_name = f"{client_name} {description.name}"
        self._attr_category = description.category
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, entry_id)},
            name=DEFAULT_NAME,
        )
        self._attr_extra_state_attributes = {}

    async def async_added_to_hass(self) -> None:
        """Call when entity about to be added to hass."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_SICKGEAR_UPDATED, self.update_state
            )
        )

    def update_state(self, args):
        """Get the latest data and updates the states."""
        match self._attr_category:
            case "backlog":
                self._attr_native_value = self._sickgear_api.get_schedule_setting(
                    self.entity_description.key
                )

            case "upcoming":
                upcoming = self._sickgear_api.get_upcoming_shows(
                    self.entity_description.key
                )
                self._attr_native_value = len(upcoming)
                self._attr_extra_state_attributes[ATTRIBUTE_KEY] = [
                    Episode(
                        show_name=episode[SHOW_NAME],
                        episode_name=episode[EPISODE_NAME],
                        episode_number="S{:0>2}E{:0>2}".format(
                            episode[SEASON_NUMBER], episode[EPISODE_NUMBER]
                        ),
                        episode_airdate=episode[AIR_DATE],
                        episode_network=episode[NETWORK],
                        episode_plot=episode[EPISODE_PLOT],
                        show_link="{}/{}/view-show?tvid_prodid=1:{}".format(
                            self._sickgear_api.sick_api.sickgear_url,
                            WEB_ROOT,
                            episode[SHOW_ID],
                        ),
                    )
                    for episode in upcoming
                ]

            case "shows":
                self._attr_native_value = self._sickgear_api.get_show_stat(
                    self.entity_description.key
                )

            case "disks":
                disks = self._sickgear_api.get_root_drives()
                disk_count = 0
                disk_info = []

                for disk in disks:
                    if disk[DISK_VALID] == 1:
                        if disk[DISK_PRIMARY] == 1:
                            default_disk_location = disk[DISK_LOCATION]
                            default_disk_info = [
                                RootDrive(
                                    free_space=disk[DISK_SPACE],
                                ),
                            ]
                        else:
                            disk_count += 1
                            disk_info += [
                                RootDrive(
                                    location=disk[DISK_LOCATION],
                                    free_space=disk[DISK_SPACE],
                                ),
                            ]

                if self.entity_description.key == "primary_disk":
                    self._attr_native_value = default_disk_location
                    self._attr_extra_state_attributes[ATTRIBUTE_KEY] = default_disk_info
                else:
                    self._attr_native_value = disk_count
                    self._attr_extra_state_attributes[ATTRIBUTE_KEY] = disk_info

        if self._attr_native_value is None:
            if self.entity_description.key == MISSING_EPISODES:
                downloads = int(self._sickgear_api.get_show_stat(DOWNLOADED_EPISODES))
                total_eps = int(self._sickgear_api.get_show_stat(TOTAL_EPISODES))
                self._attr_native_value = int(total_eps - downloads)
        self.schedule_update_ha_state()
