"""Constants for sickgear."""
from logging import Logger, getLogger
from datetime import timedelta


LOGGER: Logger = getLogger(__package__)

NAME = "SickGear"
DOMAIN = "sickgear"
VERSION = "0.0.0"
ATTRIBUTION = """
    Based on the Integration Blueprint for HACS : https://github.com/ludeeus/sickgear
    Also uses a modified version of the SABNZBd Integration : https://www.home-assistant.io/integrations/sabnzbd
    """

DEFAULT_HOST = "localhost"
DEFAULT_NAME = "SickGear"
DEFAULT_PORT = 8080
DEFAULT_SSL = False


SICKGEAR_URL = "SickGear URL"
SICKGEAR_KEY = "SickGear Key"

KEY_API = "api"
KEY_API_DATA = "api_data"
KEY_NAME = "name"

UPDATE_INTERVAL = timedelta(seconds=30)
SIGNAL_SICKGEAR_UPDATED = "sickgear_updated"


DATA_SABNZBD = "sickgear"

ATTR_API_KEY = "api_key"

ATTRIBUTE_KEY = "info"
SHOW_NAME = "show_name"
EPISODE_NAME = "ep_name"
SEASON_NUMBER = "season"
EPISODE_NUMBER = "episode"
AIR_DATE = "local_datetime"
NETWORK = "network"
WEB_ROOT = "home"

# Keys:
EPISODE_PLOT = "ep_plot"
MISSING_EPISODES = "ep_missing"
DOWNLOADED_EPISODES = "ep_downloaded"
TOTAL_EPISODES = "ep_total"
BACKLOG_LAST = "last_backlog"
BACKLOG_NEXT = "next_backlog"
BACKLOG_PAUSED = "backlog_is_paused"
BACKLOG_RUNNING = "backlog_is_running"
SHOW_ID = "showid"
SHOWS_ACTIVE = "shows_active"
SHOWS_TOTAL = "shows_total"
SHOWS_LATER = "shows_later"
SHOWS_TODAY = "shows_today"
SHOWS_SOON = "shows_soon"
SHOWS_MISSED = "shows_missed"
DISK_LOCATION = "location"
DISK_PRIMARY = "default"
DISK_VALID = "valid"
DISK_SPACE = "free_space"

BACKLOG_PAUSE = "backlog_disable"
BACKLOG_RESUME = "backlog_enable"
