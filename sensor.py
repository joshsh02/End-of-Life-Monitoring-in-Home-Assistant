import logging
from datetime import timedelta

import aiohttp
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_ON, STATE_OFF
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities, discovery_info=None):
    user_device_input = entry.data.get("input_device")

    async def async_fetch_data():

        # testing line
        _LOGGER.info("Fetching data from %s", user_device_input)

        async with aiohttp.ClientSession() as session:

            # to parse url to GET product name
            base_uri = "/".join(user_device_input.strip("/").split("/")[:-2])

            # GET release-specific data
            async with session.get(user_device_input) as release_resp:
                if release_resp.status != 200:
                    hass.async_create_task(
                        hass.services.async_call(
                            "persistent_notification",
                            "create",
                            {
                                "title": "EOL Tracker URI Error",
                                "message": f"URI '{user_device_input}' not found or returned an error."
                            }
                        )
                    )
                    return None

                release_data = await release_resp.json()

            # GET product-specific data (ie, specifically iphone family)
            async with session.get(base_uri) as product_resp:
                if product_resp.status != 200:
                    hass.async_create_task(
                        hass.services.async_call(
                            "persistent_notification",
                            "create",
                            {
                                "title": "EOL Tracker URI Error",
                                "message": f"URI '{user_device_input}' not found or returned an error."
                            }
                        )
                    )
                    return None

                product_data = await product_resp.json()

                return {
                    "release": release_data.get("result", {}),
                    "product": product_data.get("result", {}),
                }

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="eol_tracker",
        update_method = async_fetch_data,
        update_interval = timedelta(seconds = 300),
    )

    await coordinator.async_config_entry_first_refresh()
    data = coordinator.data
    release_info = data.get("release", {})
    product_info = data.get("product", {})

    if data is None:
        return

    label = release_info.get("label", "Unknown")
    product_name = product_info.get("label", "Unknown")

    entry_id = entry.entry_id

    entities = [
        EolSensor(coordinator, product_name, label, entry_id),
        BooleanEolSensor(coordinator, product_name, label, "LTS", release_info.get("isLts", False), entry_id),
        BooleanEolSensor(coordinator, product_name, label, "EOL", release_info.get("isEol", False), entry_id),
        BooleanEolSensor(coordinator, product_name, label, "Discontinued", release_info.get("isDiscontinued", False), entry_id),
        BooleanEolSensor(coordinator, product_name, label, "Maintained", release_info.get("isMaintained", True), entry_id),
    ]

    async_add_entities(entities)

class EolSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, name, product, entry_id):
        super().__init__(coordinator)
        self._product = f"{name} {product}"
        self._attr_name = f"{name} {product}"
        self._attr_unique_id = f"{entry_id}_{product}".lower().replace(" ", "_")
        self._entry_id = entry_id

        self._attr_device_info = {
            "identifiers": {("eol", f"{entry_id}_{self._product}")},
            "name": f"{self._product} EOL",
            "manufacturer": "endoflife.date",
            "model": self._product,
            "entry_type": "service",
        }

    @property
    def state(self):
        return self.coordinator.data.get("release", {}).get("releaseDate")

    @property
    def device_class(self):
        return "timestamp"

    @property
    def entity_picture(self):
        return self.coordinator.data.get("product", {}).get("links", {}).get("icon")

    @property
    def extra_state_attributes(self):
        release_info = self.coordinator.data.get("release", {})
        product_info = self.coordinator.data.get("product", {})
        custom_attr = release_info.get("custom", {})

        supported_os = None
        if isinstance(custom_attr, dict):
            supported_os = next(iter(custom_attr.values()), None)

        return {
            "Release Date:": release_info.get("releaseDate", "Unknown"),
            "Latest:": release_info.get("latest", "Unknown"),
            "End of Life from:": release_info.get("eolFrom", "Unknown"),
            "endoflife.date link:": product_info.get("links", {}).get("html"),
            "Release Policy:": product_info.get("links", {}).get("releasePolicy"),
            "Supported OS Versions:": supported_os,
        }


class BooleanEolSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, product_name, product, state, value, entry_id):
        super().__init__(coordinator)
        self._product = f"{product_name} {product}"
        self._state = state
        self._value = value
        self._attr_name = f"{state}"
        self._attr_unique_id = f"{entry_id}_{product_name}_{product}_{state}".lower().replace(" ", "_")

        self._attr_icon = "mdi:check-circle" if value else "mdi:close-circle"
        self._attr_native_value = "Yes" if value else "No"

        self._attr_device_info = {
            "identifiers": {("eol", f"{entry_id}_{self._product}")},
            "name": f"{self._product} EOL",
            "manufacturer": "endoflife.date",
            "model": self._product,
            "entry_type": "service",
        }

    @property
    def state(self):
        return self._attr_native_value

    @property
    def device_class(self):
        return "running"

    @property
    def extra_state_attributes(self):
        return {"name": self._attr_name}