
from .core import run_command

def devices():
    return run_command("adb devices")

def devices_long():
    return run_command("adb devices -l")

def root():
    return run_command("adb root")

def start_server():
    return run_command("adb start-server")

def kill_server():
    return run_command("adb kill-server")

def reboot():
    return run_command("adb reboot")

def shell():
    return run_command("adb shell")

def help():
    return run_command("adb help")

def custom_command(device_id, command):
    return run_command(f"adb -s {device_id} {command}")

def usb_only(command):
    return run_command(f"adb -d {command}")

def emulator_only(command):
    return run_command(f"adb -e {command}")
