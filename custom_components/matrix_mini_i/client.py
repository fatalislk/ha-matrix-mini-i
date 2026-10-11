"""MADS 协议客户端：一条常连 TCP，JSON + CRLF 帧。"""
from __future__ import annotations

import asyncio
import json
import logging

_LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = 8890
MAX_BUFFER = 512_000


class MiniIError(Exception):
    """通用错误。"""


class MiniIClient:
    """保持一条到设备的 socket，串行发命令。"""

    def __init__(self, host: str, port: int = DEFAULT_PORT, timeout: float = 5.0) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._lock = asyncio.Lock()

    # ---------- 连接管理 ----------

    @property
    def connected(self) -> bool:
        return self._writer is not None and not self._writer.is_closing()

    async def _async_connect(self) -> None:
        if self.connected:
            return
        _LOGGER.debug("连接 %s:%s", self.host, self.port)
        self._reader, self._writer = await asyncio.wait_for(
            asyncio.open_connection(self.host, self.port), self.timeout
        )
        # 设备连上就发问候（{"errorcode":0,...}\r\nOK\r\n），先吃掉
        try:
            await asyncio.wait_for(self._async_read_reply(), self.timeout)
        except (TimeoutError, asyncio.TimeoutError):
            _LOGGER.debug("没读到问候，继续")

    async def async_close(self) -> None:
        writer, self._writer, self._reader = self._writer, None, None
        if writer is not None:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:  # noqa: BLE001
                pass

    async def _async_reset(self) -> None:
        await self.async_close()

    # ---------- 收发 ----------

    async def _async_read_reply(self) -> dict:
        assert self._reader is not None
        buf = b""
        while not buf.endswith(b"OK\r\n"):
            chunk = await self._reader.read(65536)
            if not chunk:
                raise MiniIError("设备断开了连接")
            buf += chunk
            if len(buf) > MAX_BUFFER:
                break
        first = buf.split(b"\r\n", 1)[0].strip()
        if not first:
            return {}
        try:
            return json.loads(first.decode())
        except ValueError as err:
            raise MiniIError(f"回复不是 JSON: {first[:120]!r}") from err

    async def async_command(self, cmd: str, **fields) -> dict:
        """发一条命令，返回解析后的回复。失败时断开连接（下次自动重连）。"""
        async with self._lock:
            msg = {"cmd": cmd}
            msg.update(fields)
            payload = (json.dumps(msg, ensure_ascii=False) + "\r\n").encode()
            last_err: Exception | None = None
            for attempt in (1, 2):  # 断线重连一次
                try:
                    await self._async_connect()
                    assert self._writer is not None
                    self._writer.write(payload)
                    await self._writer.drain()
                    return await asyncio.wait_for(
                        self._async_read_reply(), self.timeout
                    )
                except (MiniIError, OSError, TimeoutError, asyncio.TimeoutError) as err:
                    last_err = err
                    _LOGGER.debug("命令 %s 第 %s 次失败: %s", cmd, attempt, err)
                    await self._async_reset()
            raise MiniIError(f"命令 {cmd} 失败: {last_err}")

    # ---------- 业务封装 ----------

    async def async_status(self) -> dict:
        """读全量状态。"""
        reply = await self.async_command("get-dac-status", data={})
        data = reply.get("data")
        if not isinstance(data, dict):
            raise MiniIError(f"状态回复异常: {reply}")
        return data

    async def async_set(self, cmd: str, value: str, key: str = "set-value") -> None:
        reply = await self.async_command(cmd, **{key: str(value)})
        if reply.get("errorcode") != 0:
            raise MiniIError(f"{cmd} 返回 {reply.get('errorcode')}")

    async def async_set_power(self, on: bool) -> None:
        await self.async_set("set-key-power", "power-on" if on else "standby")

    async def async_set_mute(self, mute: bool) -> None:
        await self.async_set("set-key-mute", "mute" if mute else "unmute")

    async def async_set_volume(self, volume: int) -> None:
        await self.async_set("set-key-vol", str(int(volume)), key="set-num")

    async def async_set_input(self, source: str) -> None:
        await self.async_set("set-key-input", source)

    async def async_set_output(self, output: str) -> None:
        await self.async_set("set-key-output", output)

    async def async_set_pcm_filter(self, name: str) -> None:
        await self.async_set("set-key-pcm-filter", name)

    async def async_set_dsd_filter(self, name: str) -> None:
        await self.async_set("set-key-dsd-filter", name)

    async def async_set_dimmer(self, value: int) -> None:
        await self.async_set("set-key-dimmer", str(int(value)))
