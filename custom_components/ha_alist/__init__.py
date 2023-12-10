from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .alist import Alist
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:

    alist = Alist(hass, entry.data)
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = alist

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id)
    if len(hass.config_entries.async_entries(DOMAIN)) == 0:
        hass.data.pop(DOMAIN)
    
    return True

