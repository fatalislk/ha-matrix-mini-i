"""音量（0-100）。"""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
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
    async_add_entities([MiniIVolumeNumber(coordinator, entry)])


class MiniIVolumeNumber(MiniIEntity, NumberEntity):
    """音量。"""

    _attr_name = "mini-i Pro 4 音量"
    _attr_icon = "mdi:volume-high"
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "%"
    _attr_mode = NumberMode.SLIDER

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_volume"

    @property
    def native_value(self) -> float | None:
        value = (self.coordinator.data or {}).get("volume")
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_send_and_refresh(
            self.coordinator.client.async_set_volume(value),
            expect=lambda d: str(d.get("volume")) == str(int(value)),
        )
