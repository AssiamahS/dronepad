# DronePad

Fly a quadcopter with the PS4 controller you already own. Two halves:

1. **The sim** — https://assiamahs.github.io/dronepad/ — a browser quadcopter you can fly tonight.
   Pair the DualShock 4 over Bluetooth (hold **Share + PS** until the light bar flashes, then pick
   "Wireless Controller" in Bluetooth settings), open the link in Safari or Chrome, press any button.
   Works on the Mac and on iPhone/iPad Safari. Keyboard fallback if no pad.
2. **The bridge** — `bridge/fly_tello.py` — the same stick mapping driving a real drone.

## Sim controls (Mode 2, the way real drone radios are set up)

| Input | Does |
| --- | --- |
| Left stick up/down | Throttle. Centre = hover. Gamepad sticks self-centre, so centre is hover, not zero thrust (the "throttle floor" every PS4-drone build needs). |
| Left stick left/right | Yaw |
| Right stick | Pitch / roll |
| △ / Y, or **C** | Chase cam ↔ FPV cam (FPV has the 20° uptilt real quads use) |
| □ / X, or **M** | Angle mode (self-levels, beginner) ↔ Acro mode (rates, what FPV pilots fly) |
| Options / Share, or **R** | Reset |
| Tester button | Live view of every axis and button, for checking the mapping on a new pad |

Eight orange gates make a lap; the HUD times it and keeps your best.

## Real drones: what takes a gamepad

| Drone | Gamepad path | Cost | Verdict |
| --- | --- | --- | --- |
| **Ryze/DJI Tello** | Wi‑Fi SDK, `bridge/fly_tello.py` (this repo) | ~$75–100 refurbished; discontinued at DJI, still on eBay/Best Buy | **Start here.** Proven PS4 build with 1.4k upvotes ([r/raspberry_pi](https://www.reddit.com/r/raspberry_pi/comments/rvpqa9/control_dji_tello_drone_with_ps4_controller_and/), [Tom's Hardware](https://www.tomshardware.com/news/raspberry-pi-ps4-controller-for-drones)). |
| **Any ArduPilot / PX4 drone** (Holybro, CubePilot, home‑built) | Free ground station: QGroundControl, Mission Planner or MAVProxy joystick mode over telemetry radio | $300+ | Native. DualShock 4 confirmed via QGC ([ArduPilot forum](https://discuss.ardupilot.org/t/using-ps-gamepad-with-qgc-indoors/98106)). |
| **Skydio** (X10 etc.) | Remote Flight Deck has a beta gamepad mode, "also try a PS4 or Xbox controller" ([Skydio](https://support.skydio.com/hc/en-us/articles/18264610421915-How-to-use-Remote-Flight-Deck-with-a-gamepad-controller)) | enterprise $ | Native but not a hobby purchase. |
| **Betaflight FPV quads** | DIY only: pad → Raspberry Pi → MSP serial into the flight controller, failsafes disabled ([write‑up](https://jordancormack.github.io/DS4/)) | $150+ | Not recommended by Betaflight devs. Buy a real radio (RadioMaster Pocket, ELRS) instead; its built‑in Bluetooth joystick mode also drives every PC sim ([Oscar Liang](https://oscarliang.com/betaflight-fc-fpv-simulator)). |
| **DJI Mini/Air/Mavic** | None. The SDK is tied to DJI's own RC; no public gamepad path. | — | Skip for this project. |

## Flying the Tello

```sh
python3 -m venv ~/.dronepad && . ~/.dronepad/bin/activate
pip install djitellopy pygame
python3 bridge/fly_tello.py --dry     # controller only, prints rc values
# join the TELLO-xxxxxx Wi-Fi network, then
python3 bridge/fly_tello.py
```

✕ takes off, ○ lands, △ is emergency stop (motors off, it falls), Options quits after landing.
**Hold L1** to fly; let go and it hovers. Hold **R1** for full rate (60 % without).

## Where the research came from, and where it came up empty

Reddit and the Betaflight/ArduPilot forums had the real builds. The W3C Gamepad spec lists the
DualShock 4 under its "standard" mapping and WebKit fixed the early iOS button bugs, which is why the
sim needs no per‑pad config ([W3C](https://w3.org/TR/gamepad), [WebKit](https://bugs.webkit.org/show_bug.cgi?id=212933)).
X and Substack searches returned no usable posts on this topic; Stack Overflow had no direct hits.
Existing browser sims: [drone.js](https://github.com/zz85/drone.js) (unfinished, no FPV), FPVSIM (has a
browser build), FunPV and FPV Freestyle on itch.io. FPV pilots will tell you a gamepad is fine for
practice but won't build radio muscle memory ([IntoFPV](https://intofpv.com/printthread.php?tid=11041)); they're right.

## Repo

- `web/` — the sim, plain HTML + Three.js from cdnjs, no build step, served by GitHub Pages.
- `bridge/fly_tello.py` — gamepad → Tello, with a `--dry` mode.
- `.github/workflows/pages.yml` — syntax‑checks both, deploys `web/`.
