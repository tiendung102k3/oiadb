"""
Module for Android 14 specific accessibility support.
Provides enhanced functionality for the latest Android version.
"""

import re
import time
from .core import get_adb_instance

def is_android_14_or_higher():
    """
    Check if the connected device is running Android 14 (API level 34) or higher.
    
    Returns:
        bool: True if Android 14 or higher, False otherwise
    """
    adb = get_adb_instance()
    try:
        output = adb.run("shell getprop ro.build.version.sdk").strip()
        sdk_version = int(output)
        return sdk_version >= 34
    except:
        return False

def enable_accessibility_service():
    """
    Enable accessibility services required for XML dump on Android 14.
    
    Returns:
        bool: True if successful, False otherwise
    """
    adb = get_adb_instance()
    
    try:
        # Check current accessibility settings
        current_settings = adb.run("shell settings get secure enabled_accessibility_services").strip()
        
        # Add our service if not already enabled
        if "com.android.uiautomator.accessibility.AccessibilityService" not in current_settings:
            if current_settings and current_settings != "null":
                new_settings = current_settings + ":com.android.uiautomator.accessibility.AccessibilityService"
            else:
                new_settings = "com.android.uiautomator.accessibility.AccessibilityService"
            
            # Enable the service
            adb.run(f"shell settings put secure enabled_accessibility_services {new_settings}")
            adb.run("shell settings put secure accessibility_enabled 1")
            
            # Wait for service to start
            time.sleep(1)
        
        return True
    except:
        return False

def get_android14_ui_mode():
    """
    Get the UI mode of Android 14 device (light/dark/auto).
    
    Returns:
        str: UI mode ('light', 'dark', 'auto', or 'unknown')
    """
    adb = get_adb_instance()
    
    try:
        output = adb.run("shell settings get system ui_mode").strip()
        if output == "1":
            return "light"
        elif output == "2":
            return "dark"
        elif output == "0":
            return "auto"
        else:
            return "unknown"
    except:
        return "unknown"

def perform_android14_gesture(gesture_type, x1, y1, x2=None, y2=None, duration=None):
    """
    Perform Android 14 specific gestures using enhanced input commands.
    
    Args:
        gesture_type (str): Type of gesture ('tap', 'double_tap', 'long_press', 'swipe', 'pinch')
        x1 (int): X coordinate of first touch point
        y1 (int): Y coordinate of first touch point
        x2 (int, optional): X coordinate of second touch point (for swipe/pinch)
        y2 (int, optional): Y coordinate of second touch point (for swipe/pinch)
        duration (int, optional): Duration of gesture in milliseconds
    
    Returns:
        bool: True if successful, False otherwise
    """
    adb = get_adb_instance()
    
    try:
        if gesture_type == "tap":
            adb.run(f"shell input tap {x1} {y1}")
            return True
            
        elif gesture_type == "double_tap":
            adb.run(f"shell input tap {x1} {y1}")
            time.sleep(0.1)
            adb.run(f"shell input tap {x1} {y1}")
            return True
            
        elif gesture_type == "long_press":
            duration = duration or 1000
            adb.run(f"shell input swipe {x1} {y1} {x1} {y1} {duration}")
            return True
            
        elif gesture_type == "swipe" and x2 is not None and y2 is not None:
            duration = duration or 500
            adb.run(f"shell input swipe {x1} {y1} {x2} {y2} {duration}")
            return True
            
        elif gesture_type == "pinch" and x2 is not None and y2 is not None:
            # Android 14 supports multi-touch input through shell
            # This is a simplified implementation - in a real scenario, would use more complex multi-touch commands
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            # Pinch in (zoom out)
            adb.run(f"shell input swipe {x1} {y1} {center_x} {center_y} 300 & input swipe {x2} {y2} {center_x} {center_y} 300")
            return True
            
        return False
    except:
        return False

def handle_android14_notifications():
    """
    Handle notifications on Android 14 devices.
    
    Returns:
        list: List of current notifications
    """
    adb = get_adb_instance()
    
    try:
        # Open notification shade
        adb.run("shell cmd statusbar expand-notifications")
        time.sleep(0.5)
        
        # Get XML dump of notifications
        xml_content = adb.run("shell uiautomator dump /dev/tty")
        
        # Extract notification information
        notifications = []
        notification_pattern = r'<node[^>]*resource-id="com.android.systemui:id/notification_stack_scroller"[^>]*>(.*?)</node>'
        notification_match = re.search(notification_pattern, xml_content, re.DOTALL)
        
        if notification_match:
            notification_content = notification_match.group(1)
            
            # Extract individual notifications
            individual_pattern = r'<node[^>]*text="([^"]*)"[^>]*content-desc="([^"]*)"'
            for match in re.finditer(individual_pattern, notification_content):
                title = match.group(1)
                content = match.group(2)
                notifications.append({"title": title, "content": content})
        
        # Close notification shade
        adb.run("shell input keyevent KEYCODE_BACK")
        
        return notifications
    except:
        return []

def toggle_android14_quick_settings(setting_name):
    """
    Toggle a quick setting on Android 14 devices.
    
    Args:
        setting_name (str): Name of the setting to toggle (wifi, bluetooth, airplane, etc.)
    
    Returns:
        bool: True if successful, False otherwise
    """
    adb = get_adb_instance()
    
    try:
        # Open quick settings
        adb.run("shell cmd statusbar expand-settings")
        time.sleep(0.5)
        
        # Map setting names to content descriptions
        setting_map = {
            "wifi": "Wi-Fi",
            "bluetooth": "Bluetooth",
            "airplane": "Airplane mode",
            "flashlight": "Flashlight",
            "rotation": "Auto-rotate",
            "battery": "Battery Saver",
            "dnd": "Do Not Disturb",
            "mobile_data": "Mobile data",
            "location": "Location"
        }
        
        content_desc = setting_map.get(setting_name.lower())
        if not content_desc:
            return False
        
        # Get XML dump of quick settings
        xml_content = adb.run("shell uiautomator dump /dev/tty")
        
        # Find the setting tile
        tile_pattern = f'<node[^>]*content-desc="[^"]*{content_desc}[^"]*"[^>]*bounds="\\[(\d+),(\d+)\\]\\[(\d+),(\d+)\\]"'
        tile_match = re.search(tile_pattern, xml_content)
        
        if tile_match:
            x1, y1, x2, y2 = map(int, tile_match.groups())
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            # Tap the setting
            adb.run(f"shell input tap {center_x} {center_y}")
            time.sleep(0.5)
            
            # Close quick settings
            adb.run("shell input keyevent KEYCODE_BACK")
            return True
        
        # Close quick settings if setting not found
        adb.run("shell input keyevent KEYCODE_BACK")
        return False
    except:
        return False

def capture_android14_screenshot(output_path):
    """
    Capture screenshot on Android 14 devices with enhanced quality.
    
    Args:
        output_path (str): Path to save the screenshot
    
    Returns:
        bool: True if successful, False otherwise
    """
    adb = get_adb_instance()
    
    try:
        # Use screencap command with enhanced options for Android 14
        result = adb.run(f"shell screencap -p /sdcard/screenshot.png")
        if "error" in result.lower():
            return False
        
        # Pull the screenshot to the specified path
        adb.run(f"pull /sdcard/screenshot.png {output_path}")
        
        # Clean up
        adb.run("shell rm /sdcard/screenshot.png")
        
        return True
    except:
        return False

def get_android14_permissions_status(package_name):
    """
    Get the status of permissions for an app on Android 14.
    
    Args:
        package_name (str): Package name of the app
    
    Returns:
        dict: Dictionary of permissions and their status
    """
    adb = get_adb_instance()
    
    try:
        # Get permissions for the package
        output = adb.run(f"shell dumpsys package {package_name} | grep permission")
        
        permissions = {}
        for line in output.splitlines():
            if "granted=true" in line:
                perm_match = re.search(r'android\.permission\.([A-Z_]+)', line)
                if perm_match:
                    perm_name = perm_match.group(1)
                    permissions[perm_name] = "granted"
            elif "granted=false" in line:
                perm_match = re.search(r'android\.permission\.([A-Z_]+)', line)
                if perm_match:
                    perm_name = perm_match.group(1)
                    permissions[perm_name] = "denied"
        
        return permissions
    except:
        return {}

def grant_android14_permission(package_name, permission):
    """
    Grant a specific permission to an app on Android 14.
    
    Args:
        package_name (str): Package name of the app
        permission (str): Permission to grant (e.g., CAMERA, LOCATION)
    
    Returns:
        bool: True if successful, False otherwise
    """
    adb = get_adb_instance()
    
    try:
        # Format permission name
        if not permission.startswith("android.permission."):
            permission = f"android.permission.{permission}"
        
        # Grant the permission
        result = adb.run(f"shell pm grant {package_name} {permission}")
        
        return "error" not in result.lower()
    except:
        return False

def revoke_android14_permission(package_name, permission):
    """
    Revoke a specific permission from an app on Android 14.
    
    Args:
        package_name (str): Package name of the app
        permission (str): Permission to revoke (e.g., CAMERA, LOCATION)
    
    Returns:
        bool: True if successful, False otherwise
    """
    adb = get_adb_instance()
    
    try:
        # Format permission name
        if not permission.startswith("android.permission."):
            permission = f"android.permission.{permission}"
        
        # Revoke the permission
        result = adb.run(f"shell pm revoke {package_name} {permission}")
        
        return "error" not in result.lower()
    except:
        return False
