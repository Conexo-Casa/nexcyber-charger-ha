# NexCyber EV Charger — Home Assistant Integration

[![Home Assistant Marketplace](https://img.shields.io/badge/HA%20Marketplace-custom%20repository-41BDF5.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Conexo-Casa&repository=nexcyber-charger-ha&category=integration)
[![HA Version][ha-badge]][ha-url]

A custom integration for the **NexCyber 48A Level 2 EV
Charger** — a white-labeled Tuya device (`Smart Life` / `Tuya Smart` app,
category `qccdz`). Controls the charger over the **local network** via
[tinytuya](https://github.com/jasonacox/tinytuya) — no Tuya Cloud API, no
subscription, no expiry.

> [!IMPORTANT]
> **Support scope.** This integration was built and is maintained for the
> author's own NexCyber charger. It's shared publicly in case it helps anyone
> else with the same or a similarly white-labeled Tuya `qccdz`-category
> charger — not as a commitment to support every EV charger sold under this or
> a related brand. See [Support & Scope](#support--scope) below before opening
> an issue.

## Why local, not cloud

Tuya's Cloud Development "IoT Core" trial subscription expires (and, as of
2026, isn't reliably granted even to brand-new projects), so a Cloud
OpenAPI-based integration for a device you depend on continuously can go dark
with no warning. This integration talks to the charger directly on your LAN
instead — no external dependency, lower latency, survives Tuya's cloud being
down.

## What this exposes

Only datapoints confirmed against a real device capture are mapped — nothing
here is a guess:

| Entity | Type | Datapoint | Notes |
|---|---|---|---|
| Charging | `switch` | `switch` (18) | On/off. Pair with an HA **Schedule Helper** or automation for timed charging. |
| Charge Current Limit | `number` | `charge_cur_set` (4) | 8–48A slider. |
| Charge Mode | `select` | `work_mode` (14) | `charge_now` / `charge_pct` / `charge_energy` / `charge_schedule`. |
| Power | `sensor` | `power_total` (9) | Live load, kW. |
| Lifetime Energy | `sensor` | `forward_energy_total` (1) | kWh, feeds the HA Energy dashboard. |
| Session Energy | `sensor` | `charge_energy_once` (25) | kWh for the current session. |
| Charger Temperature | `sensor` | `temp_current` (24) | °C, diagnostic. |
| Charger State | `sensor` | `work_state` (3) | Plugged-in / charging / paused / fault, etc. |
| Pilot Signal | `sensor` | `connection_state` (13) | J1772 control-pilot voltage state, diagnostic. |

**Not exposed:** `phase_a`, `fault`, `local_timer`, `system_version`, and a
handful of fields only ever seen as Chinese-labeled events in the Tuya IoT
Platform's device log (relay/plug temperature, CP pilot voltage, session
duration, °F reading). None of these have a confirmed numeric-dpId mapping —
see [Support & Scope](#support--scope) if you'd like to help capture one.

### Scheduling

The charger's own built-in scheduler lives behind the undocumented
`local_timer` datapoint and isn't decoded. Use HA's own **Schedule Helper**
(or an automation) driving the **Charging** switch instead — same outcome,
no guessing at an undocumented byte format.

## Requirements

1. Home Assistant **2024.1** or newer.
2. The charger's **`local_key`**, **device ID**, and **LAN IP** (a DHCP
   reservation is worth setting up so the IP doesn't drift).

### Getting the local_key

`tinytuya wizard` pulls this from a linked Tuya Cloud Development project —
but that requires a *live* IoT Core subscription, which frequently isn't
available even on a freshly created project (Tuya Cloud error 28841002, "IoT
Core service subscription has expired"). If you hit that wall, use a
device-sharing app-account login tool instead — it authenticates as your
Smart Life / Tuya Smart app account directly (QR-code scan + in-app confirm)
and bypasses the Cloud Development project entirely, e.g.
[tuya-local-key](https://github.com/vineetchoudhary/tuya-local-key).

If you already have a diagnostics dump from HA's built-in `tuya` integration
(Settings → Devices → your charger → Download Diagnostics), its
`local_strategy` block has the same numeric-dpId ↔ status-code mapping used
by this integration's `const.py`.

## Installation

### Marketplace (Home Assistant 2026.11 and newer)

> [!NOTE]
> This repository is private for now. The Marketplace only adds public repositories,
> so use the manual install below until it is published.

[![Open your Home Assistant instance and show this repository in the Marketplace.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Conexo-Casa&repository=nexcyber-charger-ha&category=integration)

Or by hand:

1. Go to **Settings → Marketplace**.
2. Select **Add from link** (top right) and enter `Conexo-Casa/nexcyber-charger-ha`.
   The first time, Home Assistant asks you to connect GitHub. That is a one-time,
   read-only sign-in on github.com.
3. Open **NexCyber EV Charger** and select **Install**. The setup screen opens right away; a first
   install doesn't need a restart.

Updates show up under **Settings → Updates**. After an update, Home Assistant shows a
repair that offers to restart.

### HACS (Home Assistant 2026.10 and older)

1. HACS → **Integrations** → **⋮** → **Custom repositories**.
2. Add `https://github.com/Conexo-Casa/nexcyber-charger-ha`, category **Integration**.
3. Download **NexCyber EV Charger**, then restart Home Assistant.

An existing HACS install moves to the Marketplace by itself when you upgrade to 2026.11.

### Manual

Copy `custom_components/nexcyber_charger` into your HA config's
`custom_components/` directory and restart.

## Configuration

Settings → Devices & Services → Add Integration → **NexCyber EV Charger**.
Enter the charger's IP address, device ID, local key, and protocol version
(3.4 for this model).

## Support & Scope

This integration exists because the author owns a NexCyber 48A Level 2 EV
Charger and wanted real controls in Home Assistant beyond the single ON/OFF
exposed by Tuya's generic `qccdz`-category entity mapping. It's published here
in case it's useful to anyone else on the same white-labeled hardware — not as
a product with a support contract behind it.

In practice, that means:

- **Bug fixes are best-effort**, prioritized toward the hardware the author
  actually owns and can test against.
- **Reports about other chargers under this or a related white-label brand are
  genuinely welcome** — especially a raw DP capture (device event log, or a
  `tinytuya` raw poll) confirming an unmapped datapoint's encoding. A report
  without that kind of confirmation won't get a new field added; see the
  "Not exposed" list above for why guessing is off the table here.
- **There's no SLA, no roadmap commitment, and no guarantee any other charger
  model will ever be supported.**

**You're encouraged to fork this repository.** The code is MIT-licensed
specifically so it can be adapted for other Tuya-based EV chargers without
waiting on this repo.

## License

MIT

[ha-badge]: https://img.shields.io/badge/Home%20Assistant-2024.1%2B-41BDF5.svg
[ha-url]: https://www.home-assistant.io/
