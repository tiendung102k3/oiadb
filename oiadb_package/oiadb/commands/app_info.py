
from .core import run_command

def list_packages():
    return run_command("adb shell pm list packages")

def list_packages_r():
    return run_command("adb shell pm list packages -r")

def list_packages_3rd():
    return run_command("adb shell pm list packages -3")

def list_packages_sys():
    return run_command("adb shell pm list packages -s")

def list_packages_uninstalled():
    return run_command("adb shell pm list packages -u")

def dumpsys_package():
    return run_command("adb shell dumpsys package packages")

def dump(name):
    return run_command(f"adb shell dumpsys package {name}")

def apk_path(package):
    return run_command(f"adb shell pm path {package}")
