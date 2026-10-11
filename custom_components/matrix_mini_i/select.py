"""输入源选择。"""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, INPUT_SOURCES
from .coordinator import MiniICoordinator
from .entity import MiniIEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: MiniICoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MiniIInputSelect(coordinator, entry)])


class MiniIInputSelect(MiniIEntity, SelectEntity):
    """输入源。"""

    _attr_name = "mini-i Pro 4 输入源"
    _attr_icon = "mdi:import"
    _attr_options = INPUT_SOURCES

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_input"

    @property
    def current_option(self) -> str | None:
        value = (self.coordinator.data or {}).get("input-channel")
        if value in INPUT_SOURCES:
            return value
        return value or None

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_send_and_refresh(
            self.coordinator.client.async_set_input(option),
            expect=lambda d: d.get("input-channel") == option,
            timeout=6.0,
        )
