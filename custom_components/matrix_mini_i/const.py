"""常量。"""
from __future__ import annotations

DOMAIN = "matrix_mini_i"
MANUFACTURER = "Matrix Audio"
MODEL = "mini-i Pro 4"

DEFAULT_HOST = ""  # 由用户在配置流程里填设备 IP
DEFAULT_PORT = 8890

# 轮询间隔（秒）：走常连 socket，一次 get-dac-status 很轻
SCAN_INTERVAL = 2

# 输入源：set-key-input 的 set-value 取值，**大小写敏感**（设备原样回写进 input-channel）。
# 实测（mini-i Pro 4，MADS 1.2.226）：usb / opt / coa / coa2 / opt2 / iis / HDMI /
# network / PHONO / ANA / ANA2 返回 errorcode 0；
# 而 "hdmi"（小写）、"bluetooth"、"airplay"、"dlna"、"roonready"、"spotify"、
# "tidal"、"qobuz" 一律 40997（参数不合法）—— 串流协议不是输入源，选 network 即可。
INPUT_SOURCES = [
    "usb",
    "opt",
    "coa",
    "coa2",
    "opt2",
    "iis",
    "HDMI",
    "network",
    "PHONO",
    "ANA",
    "ANA2",
]

# 设备值 -> 界面显示名（select 的 options 用显示名，回调再映射回设备值）
INPUT_SOURCE_NAMES = {
    "usb": "USB",
    "opt": "光纤",
    "coa": "同轴",
    "coa2": "同轴 2",
    "opt2": "光纤 2",
    "iis": "I2S",
    "HDMI": "HDMI ARC",
    "network": "网络串流",
    "PHONO": "唱放",
    "ANA": "模拟输入",
    "ANA2": "模拟输入 2",
}

# 顺序即下拉顺序
INPUT_SOURCE_LABELS = [INPUT_SOURCE_NAMES[value] for value in INPUT_SOURCES]
INPUT_SOURCE_VALUES = {label: value for value, label in INPUT_SOURCE_NAMES.items()}
