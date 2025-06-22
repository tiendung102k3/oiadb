
from .core import run_command

def reboot_recovery():
    return run_command("adb reboot recovery")

def reboot_fastboot():
    return run_command("adb reboot fastboot")

def screencap(path):
    return run_command(f"adb shell screencap -p {path}")

def screenrecord(path):
    return run_command(f"adb shell screenrecord {path}")

def backup_all(filename):
    return run_command(f"adb backup -apk -all -f {filename}")

def restore_backup(filename):
    return run_command(f"adb restore {filename}")

def start_activity(intent):
    return run_command(f"adb shell am start {intent}")
