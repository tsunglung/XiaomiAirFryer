"""The Xiaomi AirFryer component."""
# pylint: disable=import-error
import asyncio
import logging
from datetime import timedelta
from collections import defaultdict
from functools import partial
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_HOST,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    CONF_TOKEN,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers import discovery
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import track_time_interval
from homeassistant.util.dt import utcnow
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator


from miio import DeviceException
from .fryer_miot import FryerMiot, FryerMiotYBAF, FryerMiotSCK, FryerMiotMi

from .const import (
    ATTR_MODE,
    ATTR_TIME,
    ATTR_RECIPE_ID,
    CONF_MODEL,
    DATA_KEY,
    DATA_STATE,
    DOMAIN,
    DOMAINS,
    DEFAULT_SCAN_INTERVAL,
    MODELS_CARELI,
    MODELS_SILEN,
    MODELS_MIOT,
    MODELS_ALL_DEVICES
)

_LOGGER = logging.getLogger(__name__)

SERVICE_SCHEMA = vol.Schema(
    {
        #    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
    }
)

SERVICE_SCHEMA_START = SERVICE_SCHEMA.extend({vol.Required(ATTR_MODE): cv.string})
SERVICE_SCHEMA_TIME = SERVICE_SCHEMA.extend({vol.Required(ATTR_TIME): cv.string})
SERVICE_SCHEMA_ID = SERVICE_SCHEMA.extend({vol.Required(ATTR_RECIPE_ID): cv.string})

SERVICE_START = "start"
SERVICE_STOP = "stop"
SERVICE_PAUSE = "pause"
SERVICE_START_CUSTOM = "start_custom"
SERVICE_RESUME = "resume"
SERVICE_APPOINT_TIME = "appoint_time"
SERVICE_RECIPE_ID = "recipe_id"


async def async_setup(hass: HomeAssistant, hass_config: dict):
    """Set up the Xiaomi AirFryer Component."""

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    """ Update Optioins if available """
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """ check unload integration """
    return all([
        await hass.config_entries.async_forward_entry_unload(entry, domain)
        for domain in DOMAINS
    ])


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Support Xiaomi AirFryer Component."""
    # pylint: disable=too-many-statements, too-many-locals
    # migrate data (also after first setup) to options
    if entry.data:
        hass.config_entries.async_update_entry(entry, data={},
                                               options=entry.data)

    # add update handler
    if not entry.update_listeners:
        entry.add_update_listener(async_update_options)

    if entry.data.get(CONF_HOST, None):
        host = entry.data[CONF_HOST]
        token = entry.data[CONF_TOKEN]
        model = entry.data.get(CONF_MODEL)
        scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    else:
        host = entry.options[CONF_HOST]
        token = entry.options[CONF_TOKEN]
        model = entry.options.get(CONF_MODEL)
        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    if DATA_KEY not in hass.data:
        hass.data.setdefault(DATA_KEY, {})
        hass.data[DATA_KEY][host] = {}

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    fryer = FryerMiot(host, token, model=model)
    if model in MODELS_CARELI:
        fryer = FryerMiot(host, token, model=model)
    elif model in MODELS_SILEN:
        fryer = FryerMiotSCK(host, token, model=model)
    elif model in MODELS_MIOT:
        fryer = FryerMiotMi(host, token, model=model)
    elif model in MODELS_ALL_DEVICES:
        fryer = FryerMiot(host, token, model=model)
    hass.data[DOMAIN][host] = fryer

    # init setup for each supported domains
    for platform in DOMAINS:
        hass.async_create_task(hass.config_entries.async_forward_entry_setup(
            entry, platform))

    def update_data():
        """Fetch data from the AirFryer."""

        try:
            state = fryer.status
            _LOGGER.debug("Got new state: %s", state)
            hass.data[DATA_KEY][host][DATA_STATE] = state

            dispatcher_send(hass, "{}_updated".format(DOMAIN), host)

        except DeviceException as ex:
            dispatcher_send(hass, "{}_unavailable".format(DOMAIN), host)
            _LOGGER.error("Got exception while fetching the state: %s", ex)

    async def async_update_data():
        """Fetch data from the AirFryer using async_add_executor_job."""
        return await hass.async_add_executor_job(update_data)

    # Create update coordinator
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        # Name of the data. For logging purposes.
        name=model,
        update_method=async_update_data,
        # Polling interval. Will only be polled if there are subscribers.
        update_interval=timedelta(seconds=scan_interval),
    )

    return True
