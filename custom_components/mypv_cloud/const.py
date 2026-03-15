"""Constants for the my-PV integration."""

from datetime import timedelta

# custom_components/mypv_cloud/const.py
DOMAIN = "mypv_cloud"

CONF_SERIALNUMBER = "serialnumber"
CONF_API_TOKEN = "api_token"

DEFAULT_SCAN_INTERVAL = timedelta(seconds=60)

ATTR_POWER = "power"
ATTR_VALID_FOR_MINUTES = "valid_for_minutes"
ATTR_TIME_BOOST_OVERRIDE = "time_boost_override"
ATTR_TIME_BOOST_VALUE = "time_boost_value"
ATTR_LEGIONELLA_BOOST_BLOCK = "legionella_boost_block"

SERVICE_SET_POWER = "set_power"