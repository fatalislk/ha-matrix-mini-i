"""配置流程：填 IP / 端口。"""
from __future__ import annotations

import asyncio
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT

from .client import MiniIClient, MiniIError
from .const import DEFAULT_HOST, DEFAULT_PORT, DOMAIN, MODEL


class MiniIConfigFlow(ConfigFlow, domain=DOMAIN):
    """只问 IP 和端口。"""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            await self.async_set_unique_id(f"{host}:{port}")
            self._abort_if_unique_id_configured()
            client = MiniIClient(host, port, timeout=4)
            try:
                data = await client.async_status()
            except (MiniIError, OSError, TimeoutError, asyncio.TimeoutError):
                errors["base"] = "cannot_connect"
            else:
                await client.async_close()
                return self.async_create_entry(
                    title=data.get("servicename") or MODEL,
                    data={CONF_HOST: host, CONF_PORT: port},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                }
            ),
            errors=errors,
        )
