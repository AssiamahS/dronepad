#!/usr/bin/env python3
"""Fly a DJI/Ryze Tello with a PS4 (or any) gamepad.

Same Mode 2 mapping as the web sim: left stick throttle/yaw, right stick pitch/roll.
    ✕ (cross)   take off          ○ (circle)  land
    △ (triangle) emergency stop   Options     quit (lands first)
    L1 held      dead-man: sticks only move the drone while L1 is held

Setup (Mac):
    python3 -m venv ~/.dronepad && . ~/.dronepad/bin/activate
    pip install djitellopy pygame
    # join the TELLO-xxxxxx Wi-Fi, then:
    python3 fly_tello.py            # add --dry to print commands without a drone

The Tello SDK takes rc a b c d in -100..100 (roll, pitch, throttle, yaw) at up to 10 Hz;
we send at 20 Hz which the drone tolerates. djitellopy opens UDP 8889 for commands.
"""
import argparse
import sys
import time

import pygame

DEAD = 0.08
EXPO = 0.4
RATE_HZ = 20
MAX = 100           # Tello rc range
SLOW = 60           # cap until you hold R1 for full rate

# W3C "standard" order is what pygame reports for a DualShock 4 on macOS too.
BTN_CROSS, BTN_CIRCLE, BTN_SQUARE, BTN_TRIANGLE = 0, 1, 2, 3
BTN_L1, BTN_R1, BTN_SHARE, BTN_OPTIONS = 4, 5, 8, 9
AX_LX, AX_LY, AX_RX, AX_RY = 0, 1, 2, 3


def curve(v: float) -> float:
    """Deadband then expo, like the sim."""
    if abs(v) < DEAD:
        return 0.0
    v = (v - (1 if v > 0 else -1) * DEAD) / (1 - DEAD)
    return v * (abs(v) * EXPO + (1 - EXPO))


class DryTello:
    """Prints what the real drone would get. Use --dry to test the controller first."""
    def connect(self): print("[dry] connect")
    def takeoff(self): print("[dry] takeoff")
    def land(self): print("[dry] land")
    def emergency(self): print("[dry] EMERGENCY")
    def send_rc_control(self, a, b, c, d): print(f"[dry] rc {a:4d} {b:4d} {c:4d} {d:4d}", end="\r")
    def get_battery(self): return 100
    def end(self): print("\n[dry] end")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="no drone, print rc values")
    args = ap.parse_args()

    pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() == 0:
        print("No gamepad. Pair the PS4 pad (hold Share+PS until the light bar flashes) and retry.")
        return 2
    pad = pygame.joystick.Joystick(0)
    pad.init()
    print(f"gamepad: {pad.get_name()} ({pad.get_numaxes()} axes, {pad.get_numbuttons()} buttons)")

    if args.dry:
        tello = DryTello()
    else:
        from djitellopy import Tello
        tello = Tello()
    tello.connect()
    print(f"battery {tello.get_battery()}%")

    flying = False
    try:
        tick = 1.0 / RATE_HZ
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.JOYBUTTONDOWN:
                    if ev.button == BTN_CROSS and not flying:
                        tello.takeoff(); flying = True
                    elif ev.button == BTN_CIRCLE and flying:
                        tello.land(); flying = False
                    elif ev.button == BTN_TRIANGLE:
                        tello.emergency(); flying = False
                    elif ev.button == BTN_OPTIONS:
                        raise KeyboardInterrupt
            if flying:
                if pad.get_button(BTN_L1):          # dead-man
                    cap = MAX if pad.get_button(BTN_R1) else SLOW
                    roll = int(curve(pad.get_axis(AX_RX)) * cap)
                    pitch = int(-curve(pad.get_axis(AX_RY)) * cap)
                    thr = int(-curve(pad.get_axis(AX_LY)) * cap)
                    yaw = int(curve(pad.get_axis(AX_LX)) * cap)
                else:
                    roll = pitch = thr = yaw = 0     # hover
                tello.send_rc_control(roll, pitch, thr, yaw)
            time.sleep(tick)
    except KeyboardInterrupt:
        pass
    finally:
        if flying:
            try: tello.land()
            except Exception as e: print("land failed:", e)
        tello.end()
    return 0


if __name__ == "__main__":
    sys.exit(main())
