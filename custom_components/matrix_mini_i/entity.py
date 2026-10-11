"""设备/实体公共信息。"""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import MiniICoordinator


def device_info(entry: ConfigEntry, data: dict) -> DeviceInfo:
    """设备信息（实体都挂这一个设备，区域只需给设备设一次）。"""
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=data.get("servicename") or MODEL,
        manufacturer=MANUFACTURER,
        model=MODEL,
        sw_version=data.get("mcu-version") or None,
        configuration_url=f"http://{entry.data.get('host', '')}",
    )


class MiniIEntity(CoordinatorEntity[MiniICoordinator]):
    """带设备信息的基类。"""

    _attr_has_entity_name = False

    def __init__(self, coordinator: MiniICoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        return device_info(self._entry, self.coordinator.data or {})
