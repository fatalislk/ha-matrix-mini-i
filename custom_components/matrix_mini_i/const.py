"""常量。"""
from __future__ import annotations

DOMAIN = "matrix_mini_i"
MANUFACTURER = "Matrix Audio"
MODEL = "mini-i Pro 4"

DEFAULT_HOST = ""  # 由用户在配置流程里填设备 IP
DEFAULT_PORT = 8890

# 轮询间隔（秒）：走常连 socket，一次 get-dac-status 很轻
SCAN_INTERVAL = 2

# 输入源选项（set-key-input 的取值）
INPUT_SOURCES = [
    "usb",
    "opt",
    "coa",
    "iis",
    "hdmi",
    "bluetooth",
    "airplay",
    "dlna",
    "roonready",
    "spotify",
    "tidal",
    "qobuz",
    "phono",
]

INPUT_SOURCE_NAMES = {
    "usb": "USB",
    "opt": "光纤",
    "coa": "同轴",
    "iis": "IIS/HDMI",
    "hdmi": "HDMI ARC",
    "bluetooth": "蓝牙",
    "airplay": "AirPlay",
    "dlna": "DLNA",
    "roonready": "Roon Ready",
    "spotify": "Spotify Connect",
    "tidal": "TIDAL",
    "qobuz": "Qobuz",
    "phono": "唱放",
}
