"""状态协调器：一条常连 socket，定时拉全量状态。"""
from __future__ import annotations

import asyncio
import logging
import time
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import MiniIClient, MiniIError
from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class MiniICoordinator(DataUpdateCoordinator[dict]):
    """所有实体共用这一份状态。"""

    def __init__(self, hass: HomeAssistant, client: MiniIClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )
        self.client = client

    async def _async_update_data(self) -> dict:
        try:
            return await self.client.async_status()
        except (MiniIError, OSError, TimeoutError) as err:
            raise UpdateFailed(str(err)) from err

    async def async_send_and_refresh(self, coro, expect=None, timeout: float = 4.0,
                                     interval: float = 0.25) -> None:
        """先发命令，再短轮询等设备确认（同一条常连 socket，很轻）。

        expect(data) 返回 True 就停；设备侧本身要几秒才切换的（比如待机、开机）
        会在它真切换的那一刻立刻回写状态，而不是等下一次定时轮询。
        """
        await coro
        deadline = time.monotonic() + timeout
        while True:
            await self.async_refresh()
            if expect is None or expect(self.data or {}):
                return
            if time.monotonic() >= deadline:
                return
            await asyncio.sleep(interval)
