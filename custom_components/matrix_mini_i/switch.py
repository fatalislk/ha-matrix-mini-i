"""开关：电源（power-on / standby）与静音。"""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import MiniICoordinator
from .entity import MiniIEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: MiniICoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            MiniIPowerSwitch(coordinator, entry),
            MiniIMuteSwitch(coordinator, entry),
        ]
    )


class MiniIPowerSwitch(MiniIEntity, SwitchEntity):
    """电源：开 = power-on，关 = standby。"""

    _attr_name = "mini-i Pro 4 电源"
    _attr_icon = "mdi:power"

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_power"

    @property
    def is_on(self) -> bool:
        return (self.coordinator.data or {}).get("dac-status") == "power-on"

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_send_and_refresh(
            self.coordinator.client.async_set_power(True),
            expect=lambda d: d.get("dac-status") == "power-on",
            timeout=8.0,
        )

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_send_and_refresh(
            self.coordinator.client.async_set_power(False),
            expect=lambda d: d.get("dac-status") == "standby",
        )


class MiniIMuteSwitch(MiniIEntity, SwitchEntity):
    """静音。"""

    _attr_name = "mini-i Pro 4 静音"
    _attr_icon = "mdi:volume-off"

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_mute"

    @property
    def is_on(self) -> bool:
        return (self.coordinator.data or {}).get("mute") == "mute"

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_send_and_refresh(
            self.coordinator.client.async_set_mute(True),
            expect=lambda d: d.get("mute") == "mute",
        )

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_send_and_refresh(
            self.coordinator.client.async_set_mute(False),
            expect=lambda d: d.get("mute") == "unmute",
        )
