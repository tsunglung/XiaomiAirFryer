"""Switch of the Xiaomi AirFryer component."""
# pylint: disable=import-error
import asyncio
import logging
from datetime import timedelta

from miio import DeviceException
import voluptuous as vol

from homeassistant.components.switch import (
    ENTITY_ID_FORMAT,
    PLATFORM_SCHEMA,
    SwitchEntity,
)
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_MODE,
    CONF_HOST,
    CONF_NAME,
    CONF_TOKEN,
    CONF_DEVICE,
    CONF_MAC
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.util import slugify
from homeassistant.components.xiaomi_miio.const import (
    CONF_FLOW_TYPE,
)
from .const import (
    ATTR_FOOD_QUANTY,
    ATTR_TIME,
    ATTR_RECIPE_ID,
    ATTR_MODE,
    ATTR_MODEL,
    ATTR_TARGET_TEMPERATURE,
    ATTR_TARGET_TIME,
    CONF_MODEL,
    DATA_STATE,
    DATA_DEVICE,
    DATA_KEY,
    DEFAULT_NAME,
    DOMAIN,
    MODELS_CARELI,
    MODELS_ALL_DEVICES,
    SERVICE_APPOINT_TIME,
    SERVICE_FOOD_QUANTY,
    SERVICE_PAUSE,
    SERVICE_START,
    SERVICE_STOP,
    SERVICE_START_CUSTOM,
    SERVICE_TARGET_TIME,
    SERVICE_TARGET_TEMPERATURE,
    SERVICE_RECIPE_ID,
    SERVICE_RESUME
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)

DEFAULT_NAME = DEFAULT_NAME + " Switch"

MODE = {"Standby": 1, "Appointment": 3, "Cooking": 4}

MODE_MAF = {
    "Standby": 1,
    "Appointment": 3,
    "Cooking": 4,
    "Preheat": 5,
    "Cooked": 6,
    "PreheatFinish": 7
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_TOKEN): vol.All(cv.string, vol.Length(min=32, max=32)),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_MODEL): vol.In(MODELS_ALL_DEVICES),
    }
)

SUCCESS = ["ok"]

FEATURE_FLAGS_GENERIC = 0

SERVICE_SCHEMA = vol.Schema({vol.Optional(ATTR_ENTITY_ID): cv.entity_ids})

SERVICE_SCHEMA_START_CUSTOM = SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_MODE): vol.All(vol.In(
        ["Standby", "Appointment", "Cooking", "Preheat", "Cooked", "PreheatFinish"]))}
)

SERVICE_SCHEMA_APPOINT_TIME = SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_TIME): cv.positive_int}
)

SERVICE_SCHEMA_FOOD_QUANTY = SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_FOOD_QUANTY): cv.positive_int}
)

SERVICE_SCHEMA_RECIPE_ID = SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_RECIPE_ID): cv.string}
)

SERVICE_SCHEMA_TARGET_TIME = SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_TARGET_TIME): cv.positive_int}
)

SERVICE_SCHEMA_TARGET_TEMPERATURE = SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_TARGET_TEMPERATURE): cv.positive_int}
)

SERVICE_TO_METHOD = {
    SERVICE_START: {"method": "async_start"},
    SERVICE_STOP: {"method": "async_stop"},
    SERVICE_PAUSE: {"method": "async_pause"},
    SERVICE_RESUME: {"method": "async_resume"},
    SERVICE_START_CUSTOM: {
        "method": "async_start_custom",
        "schema": SERVICE_SCHEMA_START_CUSTOM,
    },
    SERVICE_FOOD_QUANTY: {
        "method": "async_food_quanty",
        "schema": SERVICE_SCHEMA_FOOD_QUANTY,
    },
    SERVICE_RECIPE_ID: {
        "method": "async_recipe_id",
        "schema": SERVICE_SCHEMA_RECIPE_ID,
    },
    SERVICE_APPOINT_TIME: {
        "method": "async_appoint_time",
        "schema": SERVICE_SCHEMA_APPOINT_TIME,
    },
    SERVICE_TARGET_TIME: {
        "method": "async_target_time",
        "schema": SERVICE_SCHEMA_TARGET_TIME,
    },
    SERVICE_TARGET_TEMPERATURE: {
        "method": "async_target_temperature",
        "schema": SERVICE_SCHEMA_TARGET_TEMPERATURE,
    }
}


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Import AirFryer configuration from YAML."""
    _LOGGER.warning(
        "Loading Xiaomi AirFryer Switch via platform setup is deprecated; Please remove it from your configuration"
    )
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_IMPORT},
            data=config,
        )
    )


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the switch from a config entry."""
    entities = []

    host = config_entry.options[CONF_HOST]
    token = config_entry.options[CONF_TOKEN]
    name = config_entry.title
    model = config_entry.options[CONF_MODEL]
    unique_id = config_entry.unique_id

    if config_entry.options[CONF_FLOW_TYPE] == CONF_DEVICE:
        if DATA_KEY not in hass.data:
            hass.data[DATA_KEY] = {}

        if model in MODELS_ALL_DEVICES:
            fryer = hass.data[DOMAIN][host]
            device = XiaomiAirFryer(name, fryer, config_entry, unique_id)
            entities.append(device)
            hass.data[DATA_KEY][host][DATA_DEVICE] = device
        else:
            _LOGGER.error(
                "Unsupported device found! Please create an issue at "
                "https://github.com/tsunglung/XiaomiAirFryer/issues "
                "and provide the following data: %s",
                model,
            )

        async def async_service_handler(service):
            """Map services to methods on Xiaomi AirFryer."""
            method = SERVICE_TO_METHOD.get(service.service)
            params = {
                key: value
                for key, value in service.data.items()
                if key != ATTR_ENTITY_ID
            }
            entity_ids = service.data.get(ATTR_ENTITY_ID)
            if entity_ids:
                devices = [
                    device[DATA_DEVICE]
                    for device in hass.data[DATA_KEY].values()
                    if device[DATA_DEVICE].entity_id in entity_ids
                ]
            else:
                devices = [
                    device[DATA_DEVICE]
                    for device in hass.data[DATA_KEY].values()
                ]

            update_tasks = []
            for device in devices:
                if not hasattr(device, method["method"]):
                    continue
                await getattr(device, method["method"])(**params)
                update_tasks.append(device.async_update_ha_state(True))

            if update_tasks:
                task_objects = [asyncio.create_task(task) for task in update_tasks]
                await asyncio.wait(task_objects)

        for service, _ in SERVICE_TO_METHOD.items():
            schema = SERVICE_TO_METHOD[service].get("schema", SERVICE_SCHEMA)
            hass.services.async_register(
                DOMAIN, service, async_service_handler, schema=schema
            )

    async_add_entities(entities, update_before_add=False)


class XiaomiAirFryer(SwitchEntity):
    """Representation of a Xiaomi AirFryer."""

    def __init__(self, name, device, entry, unique_id):
        """Initialize the AirFryer."""
        super().__init__()

        self._available = False
        self._state = None
        self._device = device
        self._host = entry.options[CONF_HOST]
        self._attr_name = name
        self._attr_unique_id = "{}.{}-{}".format(
            DOMAIN, unique_id, name.lower().replace(" ", "-"))
        self._device_id = unique_id
        self._model = entry.options[CONF_MODEL]
        self._mac = entry.options[CONF_MAC]
        self._state_attrs = {ATTR_MODEL: self._model}
        self._device_features = FEATURE_FLAGS_GENERIC
        self._skip_update = False

        self.entity_id = ENTITY_ID_FORMAT.format(
            "{}_{}".format(DOMAIN, slugify(name))
        )

    @property
    def icon(self):
        """Return the icon to use for device if any."""
        return "mdi:pot-mix"

    @property
    def available(self):
        """Return true when state is known."""
        return self._available

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the device."""
        return self._state_attrs

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._state

    @property
    def device_info(self):
        """Return the device info."""
        device_info = {
            "identifiers": {(DOMAIN, self._device_id)},
            "manufacturer": (self._model or "Xiaomi").split(".", 1)[0].capitalize(),
            "name": self._attr_name,
            "model": self._model,
        }

        if self._mac is not None:
            device_info["connections"] = {(dr.CONNECTION_NETWORK_MAC, self._mac)}

        return device_info

    async def async_turn_on(self, **kwargs):
        """Turn the air fryeron."""
        result = self._device.start_cook()

        if result:
            self._state = True
            self._skip_update = True

    async def async_turn_off(self, **kwargs):
        """Turn the air fryer off."""
        result = self._device.cancel_cooking()

        if result:
            self._state = False
            self._skip_update = True

    async def async_start(self):
        """Start cooking."""
        self._device.start_cook()

    async def async_stop(self):
        """Stop cooking."""
        self._device.cancel_cooking()

    async def async_pause(self):
        """Pause cooking."""
        self._device.pause()

    async def async_resume(self):
        """Resume cooking."""
        self._device.resume_cooking()

    async def async_start_custom(self, mode: str):
        """Start custom cooking."""
        if self._model in MODELS_CARELI:
            self._device.start_custom_cook(MODE_MAF[mode])
        else:
            self._device.start_custom_cook(MODE[mode])

    async def async_food_quanty(self, food_quanty: int):
        """Set food quanty."""
        self._device.food_quanty(food_quanty)

    async def async_recipe_id(self, recipe_id: str):
        """Set recipe id."""
        self._device.recipe_id(recipe_id)

    async def async_appoint_time(self, time: int):
        """Set appoint time."""
        self._device.appoint_time(time)

    async def async_target_time(self, target_time: int):
        """Set target time."""
        self._device.target_time(target_time)

    async def async_target_temperature(self, target_temperature: int):
        """Set target temperature."""
        self._device.target_temperature(target_temperature)

    async def async_update(self):
        """Fetch state from the device."""
        # On state change the device doesn't provide the new state immediately.
        if self._skip_update:
            self._skip_update = False
            return

        try:
            state = await self.hass.async_add_executor_job(self._device.status)
            _LOGGER.debug("Got new state: %s", state)
            self.hass.data[DATA_KEY][self._host][DATA_STATE] = state

            if state is not None:
                self._available = True
                self._state = state.is_on

            self.async_schedule_update_ha_state()
        except DeviceException as ex:
            if self._available:
                self._available = False
                _LOGGER.error("Got exception while fetching the state: %s", ex)

