
from .core import run_command

def logcat(options=""):
    return run_command(f"adb logcat {options}")

def bugreport():
    return run_command("adb bugreport")
