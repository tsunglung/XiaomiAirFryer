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
from .fryer_miot import FryerMiot, FryerMiotYBAF, FryerMiotSCK, FryerMiotMi, FryerMiotViomi

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
    MODELS_VIOMI,
    MODELS_ALL_DEVICES
)

_LOGGER = logging.getLogger(__name__)

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
    elif model in MODELS_VIOMI:
        fryer = FryerMiotViomi(host, token, model=model)
    elif model in MODELS_ALL_DEVICES:
        fryer = FryerMiot(host, token, model=model)
    hass.data[DOMAIN][host] = fryer

    # init setup for each supported domains
    await hass.config_entries.async_forward_entry_setups(entry, DOMAINS)

    return True
