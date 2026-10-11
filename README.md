# Matrix Audio mini-i — Home Assistant integration

Unofficial **local** integration for [Matrix Audio](https://www.matrix-digi.com/) streamers / DACs
(tested on **mini-i Pro 4**) that exposes the device's real controls to Home Assistant over its own
local control socket — no cloud, no app, no MQTT bridge.

> Not affiliated with Matrix Audio. Protocol was reverse engineered from the MA Remote app
> (APK decompilation) plus live probing of the device. Use at your own risk.

## Why this exists

The mini-i Pro 4 is already discoverable in Home Assistant:

* **DLNA/UPnP (`dlna_dmr`)** — transport controls work, but `RenderingControl` volume/mute are
  **stubs**: the device answers 200 and then ignores the value. The volume slider in HA does nothing.
* **Music Assistant** — great for playback, still can't power the DAC on/off or switch its inputs.
* **MPD (port 6600)** — has **no mixer**, so no volume either.

Meanwhile the device has a perfectly good local control protocol — that's what the MA Remote app
uses. This integration speaks it directly, so every entity reflects the device's real state, and
state changes land in Home Assistant in ~0.1–0.4 s (commands are sent on a persistent socket and the
new state is read back immediately, instead of waiting for the next poll).

## Entities

| Entity | Type | Notes |
|---|---|---|
| `switch.matrix_…` power | switch | on = `power-on`, off = `standby`. The device stays on the network while in standby, so it can be woken from HA (no WoL needed). |
| mute | switch | device mute |
| volume | number (slider) | 0–100, same scale as the device's display |
| input source | select | usb / opt / coa / iis / hdmi / bluetooth / airplay / dlna / roonready / spotify / tidal / qobuz / phono |
| status | sensor | `power-on` / `standby`, with volume / mute / input / output / filters / dimmer / standby timer as attributes |
| input, output, PCM filter, DSD filter, screen dimmer, network | sensors | read-only mirrors |

All entities belong to one HA device (area can be assigned once on the device).

## Requirements

* Home Assistant 2024.6 or newer (developed against 2026.10)
* The device on the same network, **MADS control port 8890** reachable (this is the port the MA
  Remote app uses; it is open by default)
* Tested firmware: `MADS 1.2.226` / `1.1.6 Build056` on a mini-i Pro 4. Other MA devices that run the
  same MADS stack very likely work — reports welcome.

## Installation

### HACS (recommended)

1. HACS → Integrations → ⋮ → **Custom repositories** → add
   `https://github.com/fatalislk/ha-matrix-mini-i` with category **Integration**
2. Install **Matrix Audio mini-i**, then restart Home Assistant
3. Settings → Devices & Services → **Add integration** → *Matrix Audio mini-i*
   → enter the device IP (port defaults to `8890`)

### Manual

Copy `custom_components/matrix_mini_i` into your `config/custom_components/` directory and restart
Home Assistant, then add the integration from the UI.

## Notes & limitations

* **Power-on takes a few seconds.** The device only acknowledges `power-on` after it has booted
  (~3–4 s), so the switch reports `on` when the device says so — that delay is the hardware, not the
  integration. Standby is ~1 s.
* **Background polling is 2 s** over the persistent socket; anything changed on the device's front
  panel or the remote shows up within that window. Anything you change from Home Assistant is
  confirmed immediately (the integration re-reads state until the device agrees).
* The input source list is a fixed superset — selecting a source your model doesn't have returns an
  error from the device.
* Volume is set on the device's own 0–100 scale.
* Only a subset of the protocol is exposed (power / mute / volume / input / filters / dimmer readout).
  The device exposes a lot more (standby timer, shortcut keys, output auto-switch, headphone gain
  limits, …) — see the protocol notes below if you want to extend it.

## Protocol notes (for anyone extending this)

The control channel is a plain TCP socket, **JSON + `\r\n` framing**, one command per message:

```
$ nc <device-ip> 8890
{"errorcode":0,"data":{"version":"MADS 1.2.226"}}\r\nOK\r\n      ← greeting on connect
{"cmd":"get-dac-status","data":{}}                                → full state in `data`
{"cmd":"set-key-power","set-value":"standby"}                     → {"errorcode":0,...}
{"cmd":"set-key-mute","set-value":"mute"}                         ← or "unmute"
{"cmd":"set-key-vol","set-num":"38"}
{"cmd":"set-key-input","set-value":"usb"}
{"cmd":"set-key-output","set-value":"lineout"}                    ← or "phone"
{"cmd":"set-key-pcm-filter","set-value":"Linear phase fast roll-off"}
{"cmd":"set-key-dsd-filter","set-value":"47k"}
{"cmd":"set-key-dimmer","set-value":"60"}
```

Details that cost time to figure out:

* Every message **must** end with `\r\n` (a bare `\n` is silently ignored).
* Parameters are **flat fields** on the command object (`set-value`, `set-num`, `set-ch`, `name`, …) —
  nesting them inside `data` returns error `40997`.
* Error codes: `0` ok, `40997` invalid parameters, `40998` known command but wrong usage,
  `40999` unknown command.
* The device is **still reachable while in standby** (`dac-status: standby`), which is what makes
  remote power-on possible.
* `get-dac-status` returns much more than this integration uses, e.g. `pcm-filter`, `dsd-filter`,
  `dimmer`, `standby` (auto-standby timer, seconds), `autoPowerOn`, `powerKeyMode`, `buzzer`,
  `ph-volume`, `linevol-limit-en`, `output-auto`, `shortcut-key1/2`, `CPU-temperature`,
  `network-status`, `wifi-dbm`, `audio-format`, `audio-FS`.

## 中文说明

非官方**本地**集成，把 Matrix Audio 串流解码器（在 mini-i Pro 4 上实测）的真实控制接进 Home Assistant：
电源/待机、静音、音量、输入源、滤波与屏幕亮度状态，全部走设备自己的本地控制协议（就是 MA Remote
App 用的那条），不经过云端。

**为什么需要它**：这台设备在 HA 里本来就能被发现，但 DLNA/UPnP 的音量和静音是**桩**（返回 200 却不
生效），MPD 又没有 mixer，所以在 HA 里根本调不了音量；MA Remote App 走的是另一条本地 socket
（8890）。这个集成直接说那套协议，所以状态是真的，命令发完 ~0.1–0.4 秒内 HA 状态就跟着变。

**安装**：HACS → 集成 → ⋮ → 自定义仓库 → 填本仓库地址、类别选"集成" → 安装 → 重启 HA →
设置 → 设备与服务 → 添加集成 → 填设备 IP（端口默认 8890）。

**注意**：开机需要 3~4 秒设备才应答（它在启动），所以开关会等设备确认后才显示"开"；待机约 1 秒。
后台每 2 秒轮询一次，面板/遥控器上的改动 2 秒内同步进 HA。协议细节与踩坑见上面的
Protocol notes，想扩展别的功能（待机定时、快捷键、耳机增益限制等）从那里入手。

## License

MIT — see [LICENSE](LICENSE).
