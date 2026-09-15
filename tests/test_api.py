"""Unit tests for the tinytuya wrapper — mocks tinytuya.Device, no real network I/O."""

from unittest.mock import MagicMock, patch

import pytest

from nexcyber_charger.api import NexCyberApiError, NexCyberChargerApi


@patch("nexcyber_charger.api.tinytuya.Device")
def test_get_status_returns_dps(mock_device_cls):
    mock_device = MagicMock()
    mock_device.status.return_value = {"dps": {"18": False, "9": 0}}
    mock_device_cls.return_value = mock_device

    api = NexCyberChargerApi("dev-id", "local-key", "192.168.4.155", 3.4)
    dps = api.get_status()

    assert dps == {"18": False, "9": 0}


@patch("nexcyber_charger.api.tinytuya.Device")
def test_get_status_raises_on_malformed_response(mock_device_cls):
    mock_device = MagicMock()
    mock_device.status.return_value = {"Error": "Not Found", "Err": "905"}
    mock_device_cls.return_value = mock_device

    api = NexCyberChargerApi("dev-id", "local-key", "192.168.4.155", 3.4)
    with pytest.raises(NexCyberApiError):
        api.get_status()


@patch("nexcyber_charger.api.tinytuya.Device")
def test_set_dp_raises_on_device_error(mock_device_cls):
    mock_device = MagicMock()
    mock_device.set_value.return_value = {"Error": "Key or Version Invalid"}
    mock_device_cls.return_value = mock_device

    api = NexCyberChargerApi("dev-id", "local-key", "192.168.4.155", 3.4)
    with pytest.raises(NexCyberApiError):
        api.set_dp(18, True)


@patch("nexcyber_charger.api.tinytuya.Device")
def test_set_dp_success(mock_device_cls):
    mock_device = MagicMock()
    mock_device.set_value.return_value = {"dps": {"18": True}}
    mock_device_cls.return_value = mock_device

    api = NexCyberChargerApi("dev-id", "local-key", "192.168.4.155", 3.4)
    api.set_dp(18, True)  # should not raise

    mock_device.set_value.assert_called_once_with(18, True, nowait=False)
