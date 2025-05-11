"""Sensors of the Xiaomi AirFryer component."""
# pylint: disable=import-error
import asyncio
import logging
from enum import Enum
from typing import Optional
from datetime import timedelta

from homeassistant.components.sensor import ENTITY_ID_FORMAT, SensorEntity
from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.util import slugify
from homeassistant.exceptions import PlatformNotReady
from homeassistant.const import (
    CONF_HOST,
    CONF_MAC,
    CONF_TOKEN,
    UnitOfTemperature,
    UnitOfTime,
)

from miio import Device, DeviceException
from .const import (
    CONF_MODEL,
    DATA_KEY,
    DATA_STATE,
    DOMAIN,
    MODEL_FRYER_YBAF01,
    MODELS_CARELI,
    MODELS_MIOT,
    MODELS_SILEN,
    MODELS_VIOMI,
    MODELS_ALL_DEVICES
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=10)

SENSOR_TYPES_MAF = {
    "status": ["Status", None, "status", None, "mdi:bowl", None],
    "target_time": ["Target Time", None, "target_time", UnitOfTime.MINUTES, "mdi:menu", None],
    "target_temperature": ["Target Temperature", None, "target_temperature", UnitOfTemperature.CELSIUS, None,SensorDeviceClass.TEMPERATURE],
    "left_time": ["Remaining", None, "left_time", UnitOfTime.MINUTES, "mdi:timer", None],
    "recipe_id": ["Recipe Id", None, "recipe_id", None, "mdi:rice", None],
    "appoint_time": ["Appoint Time", None, "appoint_time", UnitOfTime.MINUTES, "mdi:timelapse", None],
    "food_quanty": ["Food Quanty", None, "food_quanty", None, "mdi:flash-outline", None],
    "preheat_switch": ["Preheat Phase", None, "preheat_switch", None, "mdi:pot-steam-outline", None],
    "appoint_time_left": ["Appoint Time Left", None, "appoint_time_left", UnitOfTime.MINUTES, "mdi:timer", None],
    "turn_pot": ["Turn Pot", None, "turn_pot", None, "mdi:rotate-3d-variant", None]
}

SENSOR_TYPES_YBAF = {
    "status": ["Status", None, "status", None, "mdi:bowl", None],
    "target_time": ["Target Time", None, "target_time", None, "mdi:menu", None],
    "target_temperature": ["Target Temperature", None, "target_temperature", UnitOfTemperature.CELSIUS, None, SensorDeviceClass.TEMPERATURE],
    "left_time": ["Remaining", None, "left_time", UnitOfTime.MINUTES, "mdi:timer", None],
    "mode": ["Recipe Id", None, "mode", None, "mdi:stairs", None]
}

SENSOR_TYPES_SCK = {
    "status": ["Status", None, "status", None, "mdi:bowl", None],
    "target_time": ["Target Time", None, "target_time", None, "mdi:menu", None],
    "target_temperature": ["Target Temperature", None, "target_temperature", UnitOfTemperature.CELSIUS, None, SensorDeviceClass.TEMPERATURE],
    "left_time": ["Remaining", None, "left_time", UnitOfTime.MINUTES, "mdi:timer", None],
    "switch_status": ["Preheat Phase", None, "work_temp", None, "mdi:pot-steam-outline", None],
    "mode": ["Recipe Id", None, "mode", None, "mdi:stairs", None]
}

SENSOR_TYPES_MIOT = {
    "status": ["Status", None, "status", None, "mdi:bowl", None],
    "target_time": ["Target Time", None, "target_time", None, "mdi:menu", None],
    "target_temperature": ["Target Temperature", None, "target_temperature", UnitOfTemperature.CELSIUS, None, SensorDeviceClass.TEMPERATURE],
    "left_time": ["Remaining", None, "left_time", UnitOfTime.MINUTES, "mdi:timer", None],
    "recipe_id": ["Recipe Id", None, "recipe_id", None, "mdi:rice", None],
    "preheat_switch": ["Preheat Phase", None, "preheat_switch", None, "mdi:pot-steam-outline", None],
    "mode": ["Recipe Id", None, "mode", None, "mdi:stairs", None]
}

SENSOR_TYPES_VIOMI = {
    "status": ["Status", None, "status", None, "mdi:bowl", None],
    "target_time": ["Target Time", None, "target_time", None, "mdi:menu", None],
    "target_temperature": ["Target Temperature", None, "target_temperature", UnitOfTemperature.CELSIUS, None, SensorDeviceClass.TEMPERATURE],
    "left_time": ["Remaining", None, "left_time", UnitOfTime.MINUTES, "mdi:timer", None],
    "recipe_id": ["Recipe Id", None, "recipe_id", None, "mdi:rice", None],
    "turn_pot_status": ["Turn Pot Status", None, "turn_pot_status", None, "mdi:rotate-3d-variant", None],
}


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Import Mijia AirFryer configuration from YAML."""
    _LOGGER.warning(
        "Loading Mijia AirFryer via platform setup is deprecated;"
        " Please remove it from your configuration"
    )
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_IMPORT},
            data=config,
        )
    )

async def async_setup_entry(hass, config, async_add_devices, discovery_info=None):
    """Set up the miio fan device from config."""

    if DATA_KEY not in hass.data:
        hass.data[DATA_KEY] = {}

    if config.data.get(CONF_HOST, None):
        host = config.data[CONF_HOST]
        token = config.data[CONF_TOKEN]
        model = config.data.get(CONF_MODEL)
    else:
        host = config.options[CONF_HOST]
        token = config.options[CONF_TOKEN]
        model = config.options.get(CONF_MODEL)

    _LOGGER.info("Initializing with host %s (token %s...)", host, token[:5])

    if model is None:
        try:
            miio_device = Device(host, token)
            device_info = await hass.async_add_executor_job(miio_device.info)
            model = device_info.model
            _LOGGER.info(
                "%s %s %s detected",
                model,
                device_info.firmware_version,
                device_info.hardware_version,
            )
        except DeviceException as ex:
            raise PlatformNotReady from ex

    sensors = []
    fryer = hass.data[DOMAIN][host]
    if model == MODEL_FRYER_YBAF01:
        for stype in SENSOR_TYPES_YBAF.values():
            sensors.append(XiaomiAirFryerSensor(fryer, host, stype, config))
    elif model in MODELS_CARELI:
        for stype in SENSOR_TYPES_MAF.values():
            sensors.append(XiaomiAirFryerSensor(fryer, host, stype, config))
    elif model in MODELS_SILEN:
        for stype in SENSOR_TYPES_SCK.values():
            sensors.append(XiaomiAirFryerSensor(fryer, host, stype, config))
    elif model in MODELS_MIOT:
        for stype in SENSOR_TYPES_MIOT.values():
            sensors.append(XiaomiAirFryerSensor(fryer, host, stype, config))
    elif model in MODELS_VIOMI:
        for stype in SENSOR_TYPES_VIOMI.values():
            sensors.append(XiaomiAirFryerSensor(fryer, host, stype, config))
    elif model in MODELS_ALL_DEVICES:
        for stype in SENSOR_TYPES_YBAF.values():
            sensors.append(XiaomiAirFryerSensor(fryer, host, stype, config))
    else:
        _LOGGER.error(
            "Unsupported device found! Please create an issue at "
            "https://github.com/tsunglung/XiaomiAirFryer/issues "
            "and provide the following data: %s",
            model,
        )
        return False

    async_add_devices(sensors, update_before_add=False)


class XiaomiAirFryerSensor(SensorEntity):
    """ Xiaomi AirFryer Sensor """
    def __init__(self, device, host, config, entry):
        """Initialize sensor."""
        self._device = device
        self._host = host
        self._model = entry.options.get(CONF_MODEL)
        self._mac = entry.options[CONF_MAC]
        self._device_id = entry.unique_id
        self._device_name = entry.title
        self._attr_name = config[0]
        self._child = config[1]
        self._attr = config[2]
        self._attr_native_unit_of_measurement = config[3]
        self._icon = config[4]
        self._attr_device_class = config[5]
        self._state = None
        self._retry = 0
        self._retries = 3
        self._attr_unique_id = "{}.{}-{}".format(
            DOMAIN, entry.unique_id, self._attr_name.lower().replace(" ", "-"))

        self.entity_id = ENTITY_ID_FORMAT.format(
            "{}_{}".format(DOMAIN, slugify(self._attr_name))
        )

    @property
    def device_info(self):
        """Return the device info."""
        device_info = {
            "identifiers": {(DOMAIN, self._device_id)},
            "manufacturer": (self._model or "Xiaomi").split(".", 1)[0].capitalize(),
            "name": self._device_name,
            "model": self._model,
        }

        if self._mac is not None:
            device_info["connections"] = {(dr.CONNECTION_NETWORK_MAC, self._mac)}

        return device_info

    async def async_update(self):
        """Fetch state from the device."""
        # On state change the device doesn't provide the new state immediately.
        try:
            state = self.hass.data[DATA_KEY][self._host].get(DATA_STATE, None)

            if self._child is not None:
                state = getattr(state, self._child, None)
                # Unset state if child attribute isn't available anymore
                if state is None:
                    self._state = None

            if state is not None:
                value = getattr(state, self._attr, None)
                if isinstance(value, Enum):
                    self._state = value.name
                else:
                    self._state = value

            self.async_schedule_update_ha_state()

        except DeviceException as ex:
            self._retry = self._retry + 1
            if self._retry < self._retries:
                _LOGGER.info(
                    "Got exception while fetching the state: %s , _retry=%s",
                    ex,
                    self._retry,
                )
            else:
                _LOGGER.error(
                    "Got exception while fetching the state: %s , _retry=%s",
                    ex,
                    self._retry,
                )

    @property
    def state(self):
        """Return the state."""
        return self._state

    @property
    def icon(self) -> Optional[str]:
        """Return the icon to use in the frontend, if any."""
        return self._icon
