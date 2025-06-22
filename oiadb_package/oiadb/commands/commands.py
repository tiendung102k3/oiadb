
from .core import run_command

def set_battery_level(level):
    return run_command(f"adb shell dumpsys battery set level {level}")

def set_battery_status(status):
    return run_command(f"adb shell dumpsys battery set status {status}")

def reset_battery():
    return run_command("adb shell dumpsys battery reset")

def set_usb(n):
    return run_command(f"adb shell dumpsys battery set usb {n}")

def set_screen_resolution(res):
    return run_command(f"adb shell wm size {res}")
