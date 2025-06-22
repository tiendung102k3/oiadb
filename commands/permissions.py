
from .core import run_command

def permission_groups():
    return run_command("adb shell pm list permissions -g")

def permissions_details():
    return run_command("adb shell pm list permissions -g -r")
