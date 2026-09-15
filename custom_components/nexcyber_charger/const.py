"""Constants for the NexCyber EV Charger integration."""

DOMAIN = "nexcyber_charger"

# Config keys
CONF_HOST = "host"
CONF_DEVICE_ID = "device_id"
CONF_LOCAL_KEY = "local_key"
CONF_PROTOCOL_VERSION = "protocol_version"
DEFAULT_PROTOCOL_VERSION = 3.4

# Local network polling — no cloud rate limit to respect, but stay conservative
# since the charger's own control-pilot logic runs on the same MCU.
SCAN_INTERVAL_SECONDS = 20

# ── Confirmed Tuya datapoint IDs ──────────────────────────────────────────
# Sourced from HA's built-in `tuya` integration diagnostics dump
# (`local_strategy`) and cross-checked against a `tinytuya wizard` pull for
# this device. Datapoints with no Standard Instruction mapping (phase_a,
# fault, local_timer, system_version) and the Chinese-labeled fields seen only
# in the Tuya IoT Platform device event log (relay temp, plug temp, CP pilot
# voltage, session energy/duration, current temp in °F) are deliberately NOT
# mapped here — their raw encoding has never been confirmed against a live
# capture. Don't guess-map them; route the feature through a confirmed DP or
# an HA-side helper instead. See the home-assistant-custom-integration skill's
# tuya-local-devices reference for the full reasoning.
DP_FORWARD_ENERGY_TOTAL = 1
DP_WORK_STATE = 3
DP_CHARGE_CUR_SET = 4
DP_POWER_TOTAL = 9
DP_CONNECTION_STATE = 13
DP_WORK_MODE = 14
DP_SWITCH = 18
DP_TEMP_CURRENT = 24
DP_CHARGE_ENERGY_ONCE = 25

# Scale divisors — true value = raw / 10**scale (charge_cur_set and
# temp_current are scale 0, so the raw integer is used as-is).
SCALE_FORWARD_ENERGY_TOTAL = 100  # scale 2, kWh
SCALE_POWER_TOTAL = 1000  # scale 3, kW
SCALE_CHARGE_ENERGY_ONCE = 100  # scale 2, kWh

CHARGE_CUR_MIN = 8
CHARGE_CUR_MAX = 48

WORK_STATE_OPTIONS = [
    "charger_free",
    "charger_insert",
    "charger_free_fault",
    "charger_wait",
    "charger_charging",
    "charger_pause",
    "charger_end",
    "charger_fault",
]

WORK_MODE_OPTIONS = ["charge_now", "charge_pct", "charge_energy", "charge_schedule"]

CONNECTION_STATE_OPTIONS = [
    "controlpi_12v",
    "controlpi_12v_pwm",
    "controlpi_9v",
    "controlpi_9v_pwm",
    "controlpi_6v",
    "controlpi_6v_pwm",
    "controlpi_error",
]
