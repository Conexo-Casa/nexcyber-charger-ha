"""Verify sensor scale conversions and availability against confirmed DP values.

Uses raw values matching the device's real diagnostics dump / status log
rather than made-up numbers, so a wrong scale would actually be caught.
"""

from nexcyber_charger.sensor import SENSORS


def _description(key: str):
    for desc in SENSORS:
        if desc.key == key:
            return desc
    raise AssertionError(f"no sensor description for {key!r}")


def test_power_total_scale():
    # Real device log: "Total power  7.69kW" -> raw dp value 7690 (scale 3)
    assert _description("power_total").value_fn(7690) == 7.69


def test_forward_energy_total_scale():
    # scale 2 -> divide by 100
    assert _description("forward_energy_total").value_fn(0) == 0.0
    assert _description("forward_energy_total").value_fn(250) == 2.5


def test_charge_energy_once_scale():
    # Real diagnostics dump: charge_energy_once raw 1 (scale 2) -> 0.01 kWh
    assert _description("charge_energy_once").value_fn(1) == 0.01


def test_temp_current_passthrough():
    # scale 0 -> raw value used as-is (real dump: 46)
    assert _description("temp_current").value_fn(46) == 46


def test_work_state_and_connection_state_passthrough():
    assert _description("work_state").value_fn("charger_charging") == "charger_charging"
    assert _description("connection_state").value_fn("controlpi_9v") == "controlpi_9v"


def test_dp_ids_match_confirmed_local_strategy():
    # Cross-check against the numeric dpIds confirmed in the local_strategy
    # block pulled from HA's tuya integration diagnostics dump.
    expected = {
        "power_total": 9,
        "forward_energy_total": 1,
        "charge_energy_once": 25,
        "temp_current": 24,
        "work_state": 3,
        "connection_state": 13,
    }
    for key, dp in expected.items():
        assert _description(key).dp == dp
