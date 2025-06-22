# my_adb_lib/__init__.py

from .adb import MyADB

# Optional: expose command groups for direct access if needed
from .commands import (
    app_info,
    apps,
    basic,
    commands,
    connect,
    core,
    device_actions,
    device_info,
    file_ops,
    interaction,
    logs
)

__all__ = [
    "MyADB",
    "app_info",
    "apps",
    "basic",
    "commands",
    "connect",
    "core",
    "device_actions",
    "device_info",
    "file_ops",
    "interaction",
    "logs"
]