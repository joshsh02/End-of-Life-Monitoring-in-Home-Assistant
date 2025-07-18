import pytest
from datetime import timedelta
from types import SimpleNamespace
from .sensor import EolSensor, BooleanEolSensor


@pytest.fixture
def full_data():
    return {
        "release": {
            "label": "Ubuntu 20.04",
            "releaseDate": "2020-04-23",
            "isLts": True,
            "isEol": False,
            "isDiscontinued": False,
            "isMaintained": True,
            "latest": "20.04.6",
            "eolFrom": "2025-04-01",
            "custom": {"supported_os": "Linux"},
        },
        "product": {
            "label": "Ubuntu",
            "links": {
                "html": "https://endoflife.date/ubuntu",
                "icon": "https://endoflife.date/icons/ubuntu.png",
                "releasePolicy": "https://endoflife.date/ubuntu/policy",
            },
        },
    }


class DummyCoordinator(SimpleNamespace):
    """Minimal stub for DataUpdateCoordinator"""

    def __init__(self, data):
        super().__init__(data=data)
        self.update_interval = timedelta(minutes=5)


def test_eol_sensor_with_full_data(full_data):
    coord = DummyCoordinator(full_data)
    sensor = EolSensor(coord, "Ubuntu", "20.04", "entry123")

    assert sensor.state == "2020-04-23"
    assert sensor.device_class == "timestamp"
    assert sensor.entity_picture == "https://endoflife.date/icons/ubuntu.png"

    attrs = sensor.extra_state_attributes
    assert attrs["Release Date:"] == "2020-04-23"
    assert attrs["Latest:"] == "20.04.6"
    assert attrs["End of Life from:"] == "2025-04-01"
    assert attrs["endoflife.date link:"] == "https://endoflife.date/ubuntu"
    assert attrs["Release Policy:"] == "https://endoflife.date/ubuntu/policy"
    assert attrs["Supported OS Versions:"] == "Linux"

    assert "entry123_20.04" in sensor._attr_unique_id
    assert sensor._attr_device_info["model"] == "Ubuntu 20.04"


@pytest.mark.parametrize("value,expected", [(True, "Yes"), (False, "No")])
def test_boolean_eol_sensor_states(value, expected):
    coord = DummyCoordinator(full_data)
    bsensor = BooleanEolSensor(coord, "Ubuntu", "20.04", "LTS", value, "entry123")

    assert bsensor.state == expected
    assert bsensor.device_class == "running"
    assert bsensor.extra_state_attributes == {"name": "LTS"}
    icon = bsensor._attr_icon
    assert ("check-circle" in icon) == value
    assert ("close-circle" in icon) == (not value)


def test_missing_release_and_product():
    coord = DummyCoordinator({"release": {}, "product": {}})
    sensor = EolSensor(coord, "Test", "1.0", "entryX")

    assert sensor.state is None
    attrs = sensor.extra_state_attributes
    assert attrs["Release Date:"] == "Unknown"
    assert attrs["Supported OS Versions:"] is None
    assert attrs["endoflife.date link:"] is None


def test_custom_field_non_dict():
    data = {
        "release": {"releaseDate": "2021-01-01", "custom": "not-a-dict"},
        "product": {"links": {}},
    }
    coord = DummyCoordinator(data)
    sensor = EolSensor(coord, "Test", "1.0", "entryY")

    attrs = sensor.extra_state_attributes
    assert attrs["Supported OS Versions:"] is None


def test_device_info_consistency(full_data):
    coord = DummyCoordinator(full_data)
    sensor = EolSensor(coord, "Ubuntu", "20.04", "entryABC")
    bsensor = BooleanEolSensor(coord, "Ubuntu", "20.04", "EOL", True, "entryABC")

    assert sensor._attr_device_info["manufacturer"] == "endoflife.date"
    assert bsensor._attr_device_info["name"] == "Ubuntu 20.04 EOL"
    assert "_" in sensor._attr_unique_id
    assert sensor._attr_unique_id == sensor._attr_unique_id.lower()
