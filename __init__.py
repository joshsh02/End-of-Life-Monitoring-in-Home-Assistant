import logging

_LOGGER = logging.getLogger(__name__)
DOMAIN = "eol_tracker"

async def async_setup_entry(hass, entry):
    """Set up eol_tracker from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])