"""Config flow for Upload File."""
from __future__ import annotations

from homeassistant import config_entries

from . import DOMAIN


class UploadFileConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Upload File."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Upload File", data={})

        return self.async_show_form(step_id="user")
