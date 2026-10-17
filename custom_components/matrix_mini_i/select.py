"""输入源选择。"""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    INPUT_SOURCE_LABELS,
    INPUT_SOURCE_NAMES,
    INPUT_SOURCE_VALUES,
)
from .coordinator import MiniICoordinator
from .entity import MiniIEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: MiniICoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MiniIInputSelect(coordinator, entry)])


class MiniIInputSelect(MiniIEntity, SelectEntity):
    """输入源。

    options 用中文显示名，回调里映射回设备真实取值 —— 设备对大小写敏感
    （`hdmi` → 40997，只有 `HDMI` 有效），所以设备值必须走 const 里的映射表。
    """

    _attr_name = "mini-i Pro 4 输入源"
    _attr_icon = "mdi:import"
    _attr_options = INPUT_SOURCE_LABELS

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_input"

    @property
    def current_option(self) -> str | None:
        value = (self.coordinator.data or {}).get("input-channel")
        if not value:
            return None
        # 设备报了个映射表里没有的通道（固件新增/未知）：不返回选项外的值，
        # 否则 HA 会报 current_option 不在 options 里。
        return INPUT_SOURCE_NAMES.get(value)

    async def async_select_option(self, option: str) -> None:
        value = INPUT_SOURCE_VALUES.get(option, option)
        await self.coordinator.async_send_and_refresh(
            self.coordinator.client.async_set_input(value),
            expect=lambda d: d.get("input-channel") == value,
            timeout=6.0,
        )
