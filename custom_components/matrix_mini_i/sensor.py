"""状态传感器：状态总览（带全部属性）+ 几个单值传感器。"""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import MiniICoordinator
from .entity import MiniIEntity

# 单值传感器：(name, 状态键, icon)
SIMPLE = [
    ("mini-i Pro 4 输入源", "input-channel", "mdi:import"),
    ("mini-i Pro 4 输出", "output", "mdi:audio-input-stereo-minijack"),
    ("mini-i Pro 4 PCM 滤波", "pcm-filter", "mdi:sine-wave"),
    ("mini-i Pro 4 DSD 滤波", "dsd-filter", "mdi:sine-wave"),
    ("mini-i Pro 4 屏幕亮度", "dimmer", "mdi:brightness-6"),
    ("mini-i Pro 4 网络", "network-status", "mdi:wifi"),
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: MiniICoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = [MiniIStatusSensor(coordinator, entry)]
    entities += [
        MiniISimpleSensor(coordinator, entry, name, key, icon)
        for name, key, icon in SIMPLE
    ]
    async_add_entities(entities)


class MiniIStatusSensor(MiniIEntity, SensorEntity):
    """整机状态，属性里带完整状态字典（音量、静音、滤波…）。"""

    _attr_name = "mini-i Pro 4 状态"
    _attr_icon = "mdi:speaker"

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_status"

    @property
    def native_value(self) -> str | None:
        return (self.coordinator.data or {}).get("dac-status")

    @property
    def extra_state_attributes(self) -> dict:
        data = self.coordinator.data or {}
        return {
            "volume": data.get("volume"),
            "mute": data.get("mute"),
            "input-channel": data.get("input-channel"),
            "output": data.get("output"),
            "pcm-filter": data.get("pcm-filter"),
            "dsd-filter": data.get("dsd-filter"),
            "dimmer": data.get("dimmer"),
            "standby": data.get("standby"),
            "streaming-source": data.get("streaming-source"),
            "network-status": data.get("network-status"),
            "audio-format": data.get("audio-format"),
            "audio-FS": data.get("audio-FS"),
        }


class MiniISimpleSensor(MiniIEntity, SensorEntity):
    """单个状态字段。"""

    def __init__(self, coordinator, entry, name: str, key: str, icon: str) -> None:
        super().__init__(coordinator, entry)
        self._attr_name = name
        self._key = key
        self._attr_icon = icon

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_{self._key}"

    @property
    def native_value(self) -> str | None:
        value = (self.coordinator.data or {}).get(self._key)
        return value if value not in ("", None) else None
