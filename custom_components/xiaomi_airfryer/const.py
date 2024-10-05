"""Constants of the Xiaomi AirFryer component."""
from datetime import timedelta

DEFAULT_NAME = "Xiaomi AirFryer"
DOMAIN = "xiaomi_airfryer"
DOMAINS = ["sensor", "switch"]
DATA_KEY = "xiaomi_airfryer_data"
DATA_STATE = "state"
DATA_DEVICE = "device"

CONF_MODEL = "model"
CONF_MAC = "mac"

MODEL_FRYER_MAF01 = "careli.fryer.maf01"
MODEL_FRYER_MAF02 = "careli.fryer.maf02"
MODEL_FRYER_MAF03 = "careli.fryer.maf03"
MODEL_FRYER_MAF07 = "careli.fryer.maf07"
MODEL_FRYER_MAF10A = "careli.fryer.maf10a"
MODEL_FRYER_YBAF01 = "careli.fryer.ybaf01"
MODEL_FRYER_MAF05A = "careli.fryer.maf05a"
MODEL_FRYER_SCK501 = "silen.fryer.sck501"
MODEL_FRYER_SCK505 = "silen.fryer.sck505"
MODEL_FRYER_534 = "miot.fryer.534"
MODEL_FRYER_V3 = "viomi.fryer.v3"

OPT_MODEL = {
    MODEL_FRYER_MAF01: "Mi Smart Air Fryer China",
    MODEL_FRYER_MAF02: "Mi Smart Air Fryer Global",
    MODEL_FRYER_MAF03: "Mi Smart Air Fryer China",
    MODEL_FRYER_MAF07: "Mi Smart Air Fryer Global",
    MODEL_FRYER_MAF10A: "Mi Smart Air Fryer EU 6.5L",
    MODEL_FRYER_MAF05A: "Mi Smart Air Fryer EU",
    MODEL_FRYER_YBAF01: "Upany Air Fryer YB-02208DTW",
    MODEL_FRYER_SCK501: "Silencare AirFryer 1.8L",
    MODEL_FRYER_SCK505: "Silencare AirFryer",
    MODEL_FRYER_V3: "Viomi Smart Air Fryer Pro 6L",
}

MODELS_CARELI = [
    MODEL_FRYER_MAF01,
    MODEL_FRYER_MAF02,
    MODEL_FRYER_MAF03,
    MODEL_FRYER_MAF07,
    MODEL_FRYER_MAF10A,
    MODEL_FRYER_YBAF01,
    MODEL_FRYER_MAF05A
]
MODELS_SILEN = [
    MODEL_FRYER_SCK501,
    MODEL_FRYER_SCK505
]
MODELS_MIOT = [
    MODEL_FRYER_534
]
MODELS_VIOMI = [
    MODEL_FRYER_V3
]
MODELS_ALL_DEVICES = MODELS_CARELI + MODELS_SILEN + MODELS_MIOT + MODELS_VIOMI

ATTR_FOOD_QUANTY = "food_quanty"
ATTR_MODEL = "model"
ATTR_MODE = "mode"
ATTR_TIME = "time"
ATTR_TARGET_TIME = "target_time"
ATTR_TARGET_TEMPERATURE = "target_temperature"
ATTR_RECIPE_ID = "recipe_id"

SUCCESS = ["ok"]

DEFAULT_SCAN_INTERVAL = 30
SCAN_INTERVAL = timedelta(seconds=30)

SERVICE_START = "start"
SERVICE_STOP = "stop"
SERVICE_PAUSE = "pause"
SERVICE_START_CUSTOM = "start_custom"
SERVICE_RESUME = "resume"
SERVICE_APPOINT_TIME = "appoint_time"
SERVICE_RECIPE_ID = "recipe_id"
SERVICE_FOOD_QUANTY = "food_quanty"
SERVICE_TARGET_TIME = "target_time"
SERVICE_TARGET_TEMPERATURE = "target_temperature"
