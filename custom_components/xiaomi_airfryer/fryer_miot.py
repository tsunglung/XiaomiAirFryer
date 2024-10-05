"""
Support for Xiaomi AirFryer.

"""
import enum
from typing import Any, Dict
import logging
import click

from miio.click_common import command, format_output
from miio.device import DeviceStatus
from miio.miot_device import MiotDevice
from .const import (
    MODEL_FRYER_MAF01,
    MODEL_FRYER_MAF02,
    MODEL_FRYER_MAF03,
    MODEL_FRYER_MAF07,
    MODEL_FRYER_MAF10A,
    MODEL_FRYER_YBAF01,
    MODEL_FRYER_MAF05A,
    MODEL_FRYER_SCK501,
    MODEL_FRYER_SCK505,
    MODEL_FRYER_534,
    MODEL_FRYER_V3,
)

_LOGGER = logging.getLogger(__name__)


# http://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:air-fryer:0000A0A4:careli-maf02:1
MIOT_MAPPING = {
    MODEL_FRYER_MAF01: {
        "status": {"siid": 2, "piid": 1},  # read, notify
        "device_fault": {"siid": 2, "piid": 2},  # read, notify
        "target_time": {"siid": 2, "piid": 3},  # read, notify, write
        "target_temperature": {"siid": 2, "piid": 4},  # read, notify, write
        "left_time": {"siid": 2, "piid": 5},  # read, notify
        "recipe_id": {"siid": 3, "piid": 1},  # read, notify, write
        "work_time": {"siid": 3, "piid": 3},  # write
        "work_temp": {"siid": 3, "piid": 4},  # write
        "appoint_time": {"siid": 3, "piid": 5},  # read, notify, write
        "food_quanty": {"siid": 3, "piid": 6},  # read, notify, write
        "preheat_switch": {"siid": 3, "piid": 7},  # read, notify, write
        "appoint_time_left": {"siid": 3, "piid": 8},  # read, notify, write
        "turn_pot": {"siid": 3, "piid": 10},  # read, notify, write
        "start_cook": {"siid": 2, "aiid": 1},
        "cancel_cooking": {"siid": 2, "aiid": 2},
        "pause": {"siid": 2, "aiid": 3},
        "start_custom_cook": {"siid": 3, "aiid": 1},
        "resume_cooking": {"siid": 3, "aiid": 2}
    },
    MODEL_FRYER_MAF02: {
        "status": {"siid": 2, "piid": 1},  # read, notify
        "device_fault": {"siid": 2, "piid": 2},  # read, notify
        "target_time": {"siid": 2, "piid": 3},  # read, notify, write
        "target_temperature": {"siid": 2, "piid": 4},  # read, notify, write
        "left_time": {"siid": 2, "piid": 5},  # read, notify
        "recipe_id": {"siid": 3, "piid": 1},  # read, notify, write
        "work_time": {"siid": 3, "piid": 3},  # write
        "work_temp": {"siid": 3, "piid": 4},  # write
        "appoint_time": {"siid": 3, "piid": 5},  # read, notify, write
        "food_quanty": {"siid": 3, "piid": 6},  # read, notify, write
        "preheat_switch": {"siid": 3, "piid": 7},  # read, notify, write
        "appoint_time_left": {"siid": 3, "piid": 8},  # read, notify, write
        "turn_pot": {"siid": 3, "piid": 10},  # read, notify, write
        "start_cook": {"siid": 2, "aiid": 1},
        "cancel_cooking": {"siid": 2, "aiid": 2},
        "pause": {"siid": 2, "aiid": 3},
        "start_custom_cook": {"siid": 3, "aiid": 1},
        "resume_cooking": {"siid": 3, "aiid": 2}
    },
    MODEL_FRYER_MAF03: {
        "status": {"siid": 2, "piid": 1},  # read, notify
        "device_fault": {"siid": 2, "piid": 2},  # read, notify
        "target_time": {"siid": 2, "piid": 3},  # read, notify, write
        "target_temperature": {"siid": 2, "piid": 4},  # read, notify, write
        "left_time": {"siid": 2, "piid": 5},  # read, notify
        "recipe_id": {"siid": 3, "piid": 1},  # read, notify, write
        "work_time": {"siid": 3, "piid": 3},  # write
        "work_temp": {"siid": 3, "piid": 4},  # write
        "appoint_time": {"siid": 3, "piid": 5},  # read, notify, write
        "food_quanty": {"siid": 3, "piid": 6},  # read, notify, write
        "preheat_switch": {"siid": 3, "piid": 7},  # read, notify, write
        "appoint_time_left": {"siid": 3, "piid": 8},  # read, notify, write
        "turn_pot": {"siid": 3, "piid": 10},  # read, notify, write
        "start_cook": {"siid": 2, "aiid": 1},
        "cancel_cooking": {"siid": 2, "aiid": 2},
        "pause": {"siid": 2, "aiid": 3},
        "start_custom_cook": {"siid": 3, "aiid": 1},
        "resume_cooking": {"siid": 3, "aiid": 2}
    },
    MODEL_FRYER_MAF07: {
        "status": {"siid": 2, "piid": 1},  # read, notify
        "device_fault": {"siid": 2, "piid": 2},  # read, notify
        "target_time": {"siid": 2, "piid": 3},  # read, notify, write
        "target_temperature": {"siid": 2, "piid": 4},  # read, notify, write
        "left_time": {"siid": 2, "piid": 5},  # read, notify
        "recipe_id": {"siid": 3, "piid": 1},  # read, notify, write
        "work_time": {"siid": 3, "piid": 3},  # write
        "work_temp": {"siid": 3, "piid": 4},  # write
        "appoint_time": {"siid": 3, "piid": 5},  # read, notify, write
        "food_quanty": {"siid": 3, "piid": 6},  # read, notify, write
        "preheat_switch": {"siid": 3, "piid": 7},  # read, notify, write
        "appoint_time_left": {"siid": 3, "piid": 8},  # read, notify, write
        "turn_pot": {"siid": 3, "piid": 10},  # read, notify, write
        "start_cook": {"siid": 2, "aiid": 1},
        "cancel_cooking": {"siid": 2, "aiid": 2},
        "pause": {"siid": 2, "aiid": 3},
        "start_custom_cook": {"siid": 3, "aiid": 1},
        "resume_cooking": {"siid": 3, "aiid": 2}
    },
    MODEL_FRYER_MAF10A: {
        "status": {"siid": 2, "piid": 1},  # read, notify
        "device_fault": {"siid": 2, "piid": 2},  # read, notify
        "target_time": {"siid": 2, "piid": 3},  # read, notify, write
        "target_temperature": {"siid": 2, "piid": 4},  # read, notify, write
        "left_time": {"siid": 2, "piid": 5},  # read, notify
        "auto_keep_warm": {"siid": 2, "piid": 6},  # read, notify, write
        "current_keep_warm": {"siid": 2, "piid": 7},  # read, notify, write
        "mode": {"siid": 2, "piid": 8},  # read, notify, write
        "preheat": {"siid": 2, "piid": 9},  # read, notify, write
        "recipe_id": {"siid": 2, "piid": 10},  # read, notify, write
        "recipe_name": {"siid": 2, "piid": 11},  # read, notify, write
        "recipe_sync": {"siid": 2, "piid": 12},  # read, notify, write
        "taret_cooking_measure": {"siid": 2, "piid": 13},  # read, notify, write
        "turn_pot": {"siid": 2, "piid": 14},  # read, notify
        "turn_pot_config": {"siid": 2, "piid": 16},  # read, notify, write
        "reservation_left_time": {"siid": 2, "piid": 17},  # read, notify, write
        "cooking_weight": {"siid": 2, "piid": 18},  # read, notify, write
        "start_cook": {"siid": 2, "aiid": 1},
        "cancel_cooking": {"siid": 2, "aiid": 2},
        "pause": {"siid": 2, "aiid": 3},
        "resume_cook": {"siid": 2, "aiid": 4},
        "start_recipe_cook": {"siid": 2, "aiid": 5}
    },
    MODEL_FRYER_YBAF01: {
        "status": {"siid": 2, "piid": 1},  # read, notify
        "device_fault": {"siid": 2, "piid": 2},  # read, notify
        "target_time": {"siid": 2, "piid": 3},  # read, notify, write
        "target_temperature": {"siid": 2, "piid": 4},  # read, notify, write
        "left_time": {"siid": 2, "piid": 5},  # read, notify
        "mode": {"siid": 2, "piid": 7},  # read, notify, write
        "start_cook": {"siid": 2, "aiid": 1},
        "cancel_cooking": {"siid": 2, "aiid": 2},
        "pause": {"siid": 2, "aiid": 3}
    },
    MODEL_FRYER_MAF05A: {
        "status": {"siid": 2, "piid": 1},  # read, notify
        "device_fault": {"siid": 2, "piid": 2},  # read, notify
        "target_time": {"siid": 2, "piid": 3},  # read, notify, write
        "target_temperature": {"siid": 2, "piid": 4},  # read, notify, write
        "left_time": {"siid": 2, "piid": 5},  # read, notify
        "recipe_id": {"siid": 3, "piid": 1},  # read, notify, write
        "work_time": {"siid": 3, "piid": 3},  # write
        "work_temp": {"siid": 3, "piid": 4},  # write
        "appoint_time": {"siid": 3, "piid": 5},  # read, notify, write
        "food_quanty": {"siid": 3, "piid": 6},  # read, notify, write
        "preheat_switch": {"siid": 3, "piid": 7},  # read, notify, write
        "appoint_time_left": {"siid": 3, "piid": 8},  # read, notify, write
        "turn_pot": {"siid": 3, "piid": 10},  # read, notify, write
        "start_cook": {"siid": 2, "aiid": 1},
        "cancel_cooking": {"siid": 2, "aiid": 2},
        "pause": {"siid": 2, "aiid": 3},
        "start_custom_cook": {"siid": 3, "aiid": 1},
        "resume_cooking": {"siid": 3, "aiid": 2}
    },
    MODEL_FRYER_534: {
        "status": {"siid": 2, "piid": 1},  # read, notify
        "device_fault": {"siid": 2, "piid": 2},  # read, notify
        "target_time": {"siid": 2, "piid": 3},  # read, notify, write
        "target_temperature": {"siid": 2, "piid": 4},  # read, notify, write
        "switch_status": {"siid": 2, "piid": 5},  # read, notify, write
        "mode": {"siid": 2, "piid": 6},  # read, notify, write
        "left_time": {"siid": 2, "piid": 7},  # read, notify
        "work_temp": {"siid": 2, "piid": 8},  # read, notify
        "preheat_switch": {"siid": 2, "piid": 10},  # read, notify, write
        "recipe_id": {"siid": 2, "piid": 11},  # read, notify, write
        "start_cook": {"siid": 2, "aiid": 1},
        "cancel_cooking": {"siid": 2, "aiid": 2},
        "pause": {"siid": 2, "aiid": 3},
        "start_custom_cook": {"siid": 2, "aiid": 4}
    },
    # http://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:air-fryer:0000A0A4:silen-sck501:1
    MODEL_FRYER_SCK501: {
        "status": {"siid": 2, "piid": 1},  # read, notify
        "device_fault": {"siid": 2, "piid": 2},  # read, notify
        "target_time": {"siid": 2, "piid": 3},  # read, notify, write
        "target_temperature": {"siid": 2, "piid": 4},  # read, notify, write
        "switch_status": {"siid": 2, "piid": 5},  # read, notify, write
        "mode": {"siid": 2, "piid": 6},  # read, notify, write
        "left_time": {"siid": 2, "piid": 7},  # read, notify
        "start": {"siid": 3, "piid": 1},  # read, notify, write
        "start_cook": {"siid": 2, "aiid": 1},
    },
    # http://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:air-fryer:0000A0A4:silen-sck505:1
    MODEL_FRYER_SCK505: {
        "status": {"siid": 2, "piid": 1},  # read, notify
        "device_fault": {"siid": 2, "piid": 2},  # read, notify
        "target_time": {"siid": 2, "piid": 3},  # read, notify, write
        "target_temperature": {"siid": 2, "piid": 4},  # read, notify, write
        "switch_status": {"siid": 2, "piid": 5},  # read, notify, write
        "mode": {"siid": 2, "piid": 6},  # read, notify, write
        "left_time": {"siid": 2, "piid": 7},  # read, notify
        "start": {"siid": 3, "piid": 1},  # read, notify, write
        "start_cook": {"siid": 2, "aiid": 1},
    },
    # https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:air-fryer:0000A0A4:viomi-v3:1
    MODEL_FRYER_V3: {
        "status": {"siid": 2, "piid": 1},  # read, notify
        "device_fault": {"siid": 2, "piid": 2},  # read, notify
        "target_time": {"siid": 2, "piid": 3},  # read, notify, write
        "target_temperature": {"siid": 2, "piid": 4},  # read, notify, write
        "current_keep_warm": {"siid": 2, "piid": 5},  # read, notify, write
        "recipe_id": {"siid": 2, "piid": 6},  # read, notify, write
        "left_time": {"siid": 2, "piid": 7},  # read, notify
        "turn_pot_config": {"siid": 2, "piid": 9},  # read, notify, write
        "turn_pot": {"siid": 2, "piid": 10},  # read, notify
        "turn_pot_status": {"siid": 3, "piid": 1},  # read, notify
        "start_cook": {"siid": 2, "aiid": 1},
        "pause": {"siid": 2, "aiid": 2},
        "cancel_cooking": {"siid": 2, "aiid": 3},
    },
}


class DeviceException(Exception):
    """Exception wrapping any communication errors with the device."""


class Status(enum.Enum):
    """ Status """
    Unknown = -1
    Shutdown = 0
    Standby = 1
    Pause = 2
    Appointment = 3
    Cooking = 4
    Preheat = 5
    Cooked = 6
    PreheatFinish = 7
    PreheatPause = 8
    Pause2 = 9
    Keepwarm = 10
    KeepwarmPause = 11
    KeepwarmFinish = 12
    CrispyRoast = 13
    Degrease = 14


STATUS_MAPPING = {
    MODEL_FRYER_V3: {
        -1: Status.Unknown,
        0: Status.Shutdown,
        2: Status.Cooking,
        3: Status.Keepwarm,
        4: Status.Pause
    }
}

class DeviceFault(enum.Enum):
    """ Device Fault """
    Unknown = -1
    NoFaults = 0
    E1 = 1
    E2 = 2
    E3 = 3


class FoodQuanty(enum.Enum):
    """ Food Quanty """
    Unknown = -1
    Null = 0
    Single = 1
    Double = 2
    Half = 3
    Full = 4


class TurnPot(enum.Enum):
    """ Turn Pot """
    Unknown = -1
    NotTurnPot = 0
    SwitchOff = 1
    TurnPot = 2


class PreheatSwitch(enum.Enum):
    """ Turn Pot """
    Unknown = -1
    Null = 0
    Off = 1
    On = 2

class CookingMode(enum.Enum):
    Manual = 0
    FrenchFries = 1
    ChickenWing = 2
    Steak = 3
    LambChops = 4
    Fish = 5
    Shrimp = 6
    Vegetables = 7
    Cake = 8
    Pizza = 9
    Defrost = 10
    DriedFruit = 11
    Yogurt = 12

class CookingTexture(enum.Enum):
    NONE = 0
    CrispyRoast = 1
    TenderRoast = 2
    Degrease = 3

class FryerStatusMiot(DeviceStatus):
    """Container for status reports for Xiaomi FryerStatusMiot."""

    def __init__(self, data: Dict[str, Any], status_mapping: Dict[int, Status]) -> None:
        """
        Response of a Fryer (careli.fryer.maf02):
        {
          'id': 1,
          'result': [
            {'did': 'status', 'siid': 2, 'piid': 1, 'code': 0, 'value': 0},
            {'did': 'device_fault', 'siid': 2, 'piid': 2, 'code': 0, 'value': 0},
            {'did': 'target_time', 'siid': 2, 'piid': 3, 'code': 0, 'value': 2},
            {'did': 'target_temperature', 'siid': 4, 'piid': 4, 'code': 0, 'value': 54},
            {'did': 'left_time', 'siid': 2, 'piid': 5, 'code': 0, 'value': 0},
            {'did': 'auto_keep_warm', 'siid': 2, 'piid': 6, 'code': 0, 'value': 0},
            {'did': 'current_keep_warm', 'siid': 2, 'piid': 7, 'code': 0, 'value': 0},
            {'did': 'mode', 'siid': 2, 'piid': 8, 'code': 0, 'value': 0},
            {'did': 'preheat', 'siid': 2, 'piid': 9, 'code': 0, 'value': 0},
            {'did': 'recipe_id', 'siid': 2, 'piid': 10, 'code': 0, 'value': 0},
            {'did': 'recipe_name', 'siid': 2, 'piid': 11, 'code': 0, 'value': 0},
            {'did': 'recipe_sync', 'siid': 2, 'piid': 12, 'code': 0, 'value': 0},
            {'did': 'target_cooking_measure, 'siid': 2, 'piid': 13, 'code': 0, 'value': 0},
            {'did': 'turn_pot', 'siid': 2, 'piid': 14, 'code': 0, 'value': 1},
            {'did': 'turn_pot_config', 'siid': 2, 'piid': 15, 'code': 0, 'value': 0},
            {'did': 'texture', 'siid': 2, 'piid': 16, 'code': 0, 'value': 0},
            {'did': 'reservation_left_time', 'siid': 2, 'piid': 17, 'code': 0, 'value': 1},
            {'did': 'cooking_weight', 'siid': 2, 'piid': 18, 'code': 0, 'value': 1}
          ],
          'exe_time': 280
        }
        """
        self.data = data
        self.status_mapping = status_mapping or {}

    @property
    def is_on(self) -> bool:
        """True if device is currently on."""
        return False if self.data["status"] in [0, 1, 6, 9] else True

    @property
    def mode(self) -> int:
        """Mode."""
        return self.data.get("mode")

    @property
    def status(self) -> int:
        """Operation status."""
        try:
            status_raw = self.data["status"]
            return self.status_mapping[status_raw] if status_raw in self.status_mapping else Status(self.data["status"])
        except ValueError:
            _LOGGER.error("Unknown Status (%s)", self.data["status"])
            return Status.Unknown

    @property
    def device_fault(self) -> int:
        """Device Fault."""
        try:
            return DeviceFault(self.data["device_fault"])
        except ValueError:
            _LOGGER.error("Unknown Device Fault (%s)", self.data["device_fault"])
            return DeviceFault.Unknown

    @property
    def target_time(self) -> int:
        """Target Time."""
        return self.data["target_time"]

    @property
    def target_temperature(self) -> int:
        """Target Temperature."""
        return self.data["target_temperature"]

    @property
    def left_time(self) -> int:
        """Left Time."""
        return self.data["left_time"]

    @property
    def recipe_id(self) -> str:
        """Recipe ID."""
        return self.data["recipe_id"]

    @property
    def work_time(self) -> int:
        """Work time."""
        return self.data["work_time"]

    @property
    def work_temp(self) -> int:
        """Work Temp."""
        return self.data["work_temp"]

    @property
    def appoint_time(self) -> int:
        """Appoint Time"""
        return self.data["appoint_time"]

    @property
    def food_quanty(self) -> FoodQuanty:
        """Food Quanty."""
        try:
            return FoodQuanty(self.data["food_quanty"])
        except ValueError:
            _LOGGER.error("Unknown FoodQuanty (%s)", self.data["food_quanty"])
            return FoodQuanty.Unknown

    @property
    def preheat_switch(self) -> int:
        """Preheat Switch"""
        try:
            return PreheatSwitch(self.data["preheat_switch"])
        except ValueError:
            _LOGGER.error("Unknown PreheatSwitch (%s)", self.data["preheat_switch"])
            return PreheatSwitch.Unknown

    @property
    def appoint_time_left(self) -> int:
        """Appoint Time"""
        return self.data["appoint_time_left"]

    @property
    def turn_pot(self) -> TurnPot:
        """Turn Pot"""
        try:
            return TurnPot(self.data["turn_pot"])
        except ValueError:
            _LOGGER.error("Unknown TurnPot (%s)", self.data["turn_pot"])
            return TurnPot.Unknown


class FryerMiot(MiotDevice):
    """Interface for AirFryer (careli.fryer.maf02)"""
    mapping = MIOT_MAPPING[MODEL_FRYER_MAF02]
    status_mapping = None

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_FRYER_MAF02,
    ) -> None:
        if model not in MIOT_MAPPING:
            raise DeviceException("Invalid FryerMiot model: %s" % model)

        super().__init__(ip, token, start_id, debug, lazy_discover)
        self._model = model

    @command(
        default_output=format_output(
            "",
            "Status: {result.status.name}\n"
            "Device Fault: {result.device_fault.name}\n"
            "Target Time: {result.target_time}\n"
            "Target Temperature: {result.target_temperature}\n"
            "Left Time: {result.left_time}\n"
            "Recipe ID: {result.recipe_id}\n"
            "Work Time: {result.work_time}\n"
            "Work Temperature: {result.work_temp}\n"
            "Appoint Time: {result.appoint_time}\n"
            "Food Quanty: {result.food_quanty.name}\n"
            "Preheat Switch: {result.preheat_switc.name}\n"
            "Appoint Time Left: {result.appoint_time_left}\n"
            "Turn Pot: {result.turn_pot.name}\n",
        )
    )
    def status(self) -> FryerStatusMiot:
        """Retrieve properties."""
        return FryerStatusMiot(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping()
            },
            self.status_mapping
        )

    @command(
        click.argument("hours", type=int),
        default_output=format_output("Setting appoint time to {hours} hours"),
    )
    def appoint_time(self, hours: int):
        """Set appoint time hours."""
        if hours < 0 or hours > 24 * 60:
            raise DeviceException("Invalid value for a appoint time: %s" % hours)

        return self.set_property("appoint_time", hours)

    @command(
        click.argument("recipe_id", type=str),
        default_output=format_output("Setting recipe id to {recipe_id}"),
    )
    def recipe_id(self, recipe_id: str):
        """Set recipe id."""
        return self.set_property("recipe_id", recipe_id)

    @command(
        click.argument("food_quanty", type=int),
        default_output=format_output("Setting food quanty to {food_quanty}"),
    )
    def food_quanty(self, food_quanty: int):
        """Set recipe id."""
        if food_quanty < 0 or food_quanty > 5:
            raise DeviceException("Invalid value for food_quanty: %s" % food_quanty)
        return self.set_property("food_quanty", food_quanty)

    @command(
        click.argument("target_time", type=int),
        default_output=format_output("Setting target time to {target_time}"),
    )
    def target_time(self, target_time: int):
        """Set recipe id."""
        if target_time < 1 or target_time > 1440:
            raise DeviceException("Invalid value for target_time: %s" % target_time)
        return self.set_property("target_time", target_time)

    @command(
        click.argument("target_temperature", type=int),
        default_output=format_output("Setting target temperature to {target_temperature}"),
    )
    def target_temperature(self, target_temperature: int):
        """Set recipe id."""
        if target_temperature < 40 or target_temperature > 200:
            raise DeviceException("Invalid value for target_temperature: %s" % target_temperature)
        return self.set_property("target_temperature", target_temperature)

    @command()
    def start_cook(self) -> None:
        """Start cook"""
        return self.call_action("start_cook")

    @command()
    def cancel_cooking(self) -> None:
        """Cancel cooking."""
        return self.call_action("cancel_cooking")

    @command()
    def pause(self) -> None:
        """Pause cook"""
        return self.call_action("pause")

    @command()
    def start_custom_cook(self, mode) -> None:
        """Start custom cook"""
        if mode not in [1, 3, 4, 5, 6, 7]:
            raise DeviceException("Invalid value for a mode: %s" % mode)
        return self.call_action("start_custom_cook", mode)

    @command()
    def resume_cooking(self) -> None:
        """Resume cooking."""
        return self.call_action("resume_cooking")


class FryerMiotYBAF(FryerMiot):
    """Interface for AirFryer (careli.fryer.maf02)"""
    mapping = MIOT_MAPPING[MODEL_FRYER_YBAF01]


class FryerMiotSCK(FryerMiot):
    """Interface for AirFryer (careli.fryer.maf02)"""
    mapping = MIOT_MAPPING[MODEL_FRYER_SCK505]


class FryerMiotMi(FryerMiot):
    """Interface for AirFryer (careli.fryer.maf02)"""
    mapping = MIOT_MAPPING[MODEL_FRYER_534]


class FryerMiotViomi(FryerMiot):
    """Interface for AirFryer (viomi.fryer.v3)"""
    mapping = MIOT_MAPPING[MODEL_FRYER_V3]
    status_mapping = STATUS_MAPPING[MODEL_FRYER_V3]