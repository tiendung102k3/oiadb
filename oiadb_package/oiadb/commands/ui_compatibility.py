"""
Module for enhancing interface compatibility across different Android UI versions.
Provides adaptable methods for working with various Android interfaces.
"""

import re
import time
import json
from .core import get_adb_instance
from .xml_dump import get_xml_dump, find_elements_by_criteria

# Dictionary to store UI patterns for different Android versions and OEM skins
UI_PATTERNS = {
    # Stock Android patterns
    "stock": {
        "button": ["android.widget.Button", "androidx.appcompat.widget.AppCompatButton"],
        "text_field": ["android.widget.EditText", "androidx.appcompat.widget.AppCompatEditText"],
        "checkbox": ["android.widget.CheckBox", "androidx.appcompat.widget.AppCompatCheckBox"],
        "switch": ["android.widget.Switch", "androidx.appcompat.widget.SwitchCompat"],
        "radio_button": ["android.widget.RadioButton", "androidx.appcompat.widget.AppCompatRadioButton"],
        "spinner": ["android.widget.Spinner", "androidx.appcompat.widget.AppCompatSpinner"],
        "recycler_view": ["androidx.recyclerview.widget.RecyclerView"],
        "list_view": ["android.widget.ListView"],
        "scroll_view": ["android.widget.ScrollView", "androidx.core.widget.NestedScrollView"],
        "webview": ["android.webkit.WebView"]
    },
    
    # Samsung OneUI patterns
    "samsung": {
        "button": ["android.widget.Button", "androidx.appcompat.widget.AppCompatButton", "com.samsung.android.widget.SamsungButton"],
        "text_field": ["android.widget.EditText", "androidx.appcompat.widget.AppCompatEditText", "com.samsung.android.widget.SamsungEditText"],
        "checkbox": ["android.widget.CheckBox", "androidx.appcompat.widget.AppCompatCheckBox", "com.samsung.android.widget.SamsungCheckBox"],
        "switch": ["android.widget.Switch", "androidx.appcompat.widget.SwitchCompat", "com.samsung.android.widget.SamsungSwitch"],
        "radio_button": ["android.widget.RadioButton", "androidx.appcompat.widget.AppCompatRadioButton", "com.samsung.android.widget.SamsungRadioButton"],
        "spinner": ["android.widget.Spinner", "androidx.appcompat.widget.AppCompatSpinner"],
        "recycler_view": ["androidx.recyclerview.widget.RecyclerView"],
        "list_view": ["android.widget.ListView"],
        "scroll_view": ["android.widget.ScrollView", "androidx.core.widget.NestedScrollView"],
        "webview": ["android.webkit.WebView"]
    },
    
    # Xiaomi MIUI patterns
    "xiaomi": {
        "button": ["android.widget.Button", "androidx.appcompat.widget.AppCompatButton", "miui.widget.MiuiButton"],
        "text_field": ["android.widget.EditText", "androidx.appcompat.widget.AppCompatEditText", "miui.widget.MiuiEditText"],
        "checkbox": ["android.widget.CheckBox", "androidx.appcompat.widget.AppCompatCheckBox", "miui.widget.MiuiCheckBox"],
        "switch": ["android.widget.Switch", "androidx.appcompat.widget.SwitchCompat", "miui.widget.MiuiSwitch"],
        "radio_button": ["android.widget.RadioButton", "androidx.appcompat.widget.AppCompatRadioButton"],
        "spinner": ["android.widget.Spinner", "androidx.appcompat.widget.AppCompatSpinner"],
        "recycler_view": ["androidx.recyclerview.widget.RecyclerView"],
        "list_view": ["android.widget.ListView"],
        "scroll_view": ["android.widget.ScrollView", "androidx.core.widget.NestedScrollView"],
        "webview": ["android.webkit.WebView"]
    },
    
    # Huawei EMUI patterns
    "huawei": {
        "button": ["android.widget.Button", "androidx.appcompat.widget.AppCompatButton", "com.huawei.android.widget.HwButton"],
        "text_field": ["android.widget.EditText", "androidx.appcompat.widget.AppCompatEditText", "com.huawei.android.widget.HwEditText"],
        "checkbox": ["android.widget.CheckBox", "androidx.appcompat.widget.AppCompatCheckBox", "com.huawei.android.widget.HwCheckBox"],
        "switch": ["android.widget.Switch", "androidx.appcompat.widget.SwitchCompat", "com.huawei.android.widget.HwSwitch"],
        "radio_button": ["android.widget.RadioButton", "androidx.appcompat.widget.AppCompatRadioButton"],
        "spinner": ["android.widget.Spinner", "androidx.appcompat.widget.AppCompatSpinner"],
        "recycler_view": ["androidx.recyclerview.widget.RecyclerView"],
        "list_view": ["android.widget.ListView"],
        "scroll_view": ["android.widget.ScrollView", "androidx.core.widget.NestedScrollView"],
        "webview": ["android.webkit.WebView"]
    },
    
    # Oppo ColorOS patterns
    "oppo": {
        "button": ["android.widget.Button", "androidx.appcompat.widget.AppCompatButton", "com.oppo.widget.OppoButton"],
        "text_field": ["android.widget.EditText", "androidx.appcompat.widget.AppCompatEditText", "com.oppo.widget.OppoEditText"],
        "checkbox": ["android.widget.CheckBox", "androidx.appcompat.widget.AppCompatCheckBox"],
        "switch": ["android.widget.Switch", "androidx.appcompat.widget.SwitchCompat", "com.oppo.widget.OppoSwitch"],
        "radio_button": ["android.widget.RadioButton", "androidx.appcompat.widget.AppCompatRadioButton"],
        "spinner": ["android.widget.Spinner", "androidx.appcompat.widget.AppCompatSpinner"],
        "recycler_view": ["androidx.recyclerview.widget.RecyclerView"],
        "list_view": ["android.widget.ListView"],
        "scroll_view": ["android.widget.ScrollView", "androidx.core.widget.NestedScrollView"],
        "webview": ["android.webkit.WebView"]
    },
    
    # OnePlus OxygenOS patterns
    "oneplus": {
        "button": ["android.widget.Button", "androidx.appcompat.widget.AppCompatButton"],
        "text_field": ["android.widget.EditText", "androidx.appcompat.widget.AppCompatEditText"],
        "checkbox": ["android.widget.CheckBox", "androidx.appcompat.widget.AppCompatCheckBox"],
        "switch": ["android.widget.Switch", "androidx.appcompat.widget.SwitchCompat"],
        "radio_button": ["android.widget.RadioButton", "androidx.appcompat.widget.AppCompatRadioButton"],
        "spinner": ["android.widget.Spinner", "androidx.appcompat.widget.AppCompatSpinner"],
        "recycler_view": ["androidx.recyclerview.widget.RecyclerView"],
        "list_view": ["android.widget.ListView"],
        "scroll_view": ["android.widget.ScrollView", "androidx.core.widget.NestedScrollView"],
        "webview": ["android.webkit.WebView"]
    }
}

def detect_device_manufacturer():
    """
    Detect the manufacturer of the connected Android device.
    
    Returns:
        str: Detected manufacturer (lowercase) or 'stock' if unknown
    """
    adb = get_adb_instance()
    
    try:
        # Get manufacturer information
        output = adb.run("shell getprop ro.product.manufacturer").strip().lower()
        
        if "samsung" in output:
            return "samsung"
        elif "xiaomi" in output or "redmi" in output:
            return "xiaomi"
        elif "huawei" in output or "honor" in output:
            return "huawei"
        elif "oppo" in output or "realme" in output:
            return "oppo"
        elif "oneplus" in output:
            return "oneplus"
        else:
            return "stock"
    except:
        return "stock"

def get_ui_element_classes(element_type):
    """
    Get the class names for a specific UI element type based on detected device manufacturer.
    
    Args:
        element_type (str): Type of UI element (button, text_field, checkbox, etc.)
    
    Returns:
        list: List of class names for the element type
    """
    manufacturer = detect_device_manufacturer()
    
    # Get patterns for the detected manufacturer
    patterns = UI_PATTERNS.get(manufacturer, UI_PATTERNS["stock"])
    
    # Get class names for the element type
    class_names = patterns.get(element_type, [])
    
    # Always include stock Android classes as fallback
    if manufacturer != "stock":
        stock_classes = UI_PATTERNS["stock"].get(element_type, [])
        for cls in stock_classes:
            if cls not in class_names:
                class_names.append(cls)
    
    return class_names

def find_ui_element(element_type, text=None, content_desc=None, resource_id=None, threshold=0.8):
    """
    Find a UI element of a specific type with adaptive class name detection.
    
    Args:
        element_type (str): Type of UI element (button, text_field, checkbox, etc.)
        text (str, optional): Text content to match
        content_desc (str, optional): Content description to match
        resource_id (str, optional): Resource ID to match
        threshold (float, optional): Similarity threshold for matching
    
    Returns:
        dict: First matching element or None if not found
    """
    # Get all possible class names for the element type
    class_names = get_ui_element_classes(element_type)
    
    # Try each class name until a match is found
    for class_name in class_names:
        criteria = {"class": class_name, "threshold": threshold}
        
        if text:
            criteria["value"] = text
        if content_desc:
            criteria["content_desc"] = content_desc
        if resource_id:
            criteria["id"] = resource_id
        
        elements = find_elements_by_criteria(criteria)
        
        if elements:
            return elements[0]
    
    return None

def find_all_ui_elements(element_type, text=None, content_desc=None, resource_id=None, threshold=0.8):
    """
    Find all UI elements of a specific type with adaptive class name detection.
    
    Args:
        element_type (str): Type of UI element (button, text_field, checkbox, etc.)
        text (str, optional): Text content to match
        content_desc (str, optional): Content description to match
        resource_id (str, optional): Resource ID to match
        threshold (float, optional): Similarity threshold for matching
    
    Returns:
        list: List of matching elements
    """
    # Get all possible class names for the element type
    class_names = get_ui_element_classes(element_type)
    
    all_elements = []
    
    # Try each class name and collect all matches
    for class_name in class_names:
        criteria = {"class": class_name, "threshold": threshold}
        
        if text:
            criteria["value"] = text
        if content_desc:
            criteria["content_desc"] = content_desc
        if resource_id:
            criteria["id"] = resource_id
        
        elements = find_elements_by_criteria(criteria)
        all_elements.extend(elements)
    
    return all_elements

def click_ui_element(element_type, text=None, content_desc=None, resource_id=None, threshold=0.8):
    """
    Click on a UI element of a specific type with adaptive class name detection.
    
    Args:
        element_type (str): Type of UI element (button, text_field, checkbox, etc.)
        text (str, optional): Text content to match
        content_desc (str, optional): Content description to match
        resource_id (str, optional): Resource ID to match
        threshold (float, optional): Similarity threshold for matching
    
    Returns:
        bool: True if successful, False otherwise
    """
    element = find_ui_element(element_type, text, content_desc, resource_id, threshold)
    
    if not element:
        return False
    
    # Extract bounds
    bounds = element.get('bounds', '')
    bounds_match = re.search(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds)
    if not bounds_match:
        return False
    
    x1, y1, x2, y2 = map(int, bounds_match.groups())
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    
    adb = get_adb_instance()
    adb.run(f"shell input tap {center_x} {center_y}")
    
    return True

def input_text_to_element(element_type, text, input_value, content_desc=None, resource_id=None, threshold=0.8):
    """
    Input text to a UI element of a specific type with adaptive class name detection.
    
    Args:
        element_type (str): Type of UI element (usually text_field)
        text (str, optional): Text content to match
        input_value (str): Text to input
        content_desc (str, optional): Content description to match
        resource_id (str, optional): Resource ID to match
        threshold (float, optional): Similarity threshold for matching
    
    Returns:
        bool: True if successful, False otherwise
    """
    element = find_ui_element(element_type, text, content_desc, resource_id, threshold)
    
    if not element:
        return False
    
    # Extract bounds
    bounds = element.get('bounds', '')
    bounds_match = re.search(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds)
    if not bounds_match:
        return False
    
    x1, y1, x2, y2 = map(int, bounds_match.groups())
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    
    adb = get_adb_instance()
    
    # First tap to focus
    adb.run(f"shell input tap {center_x} {center_y}")
    time.sleep(0.5)
    
    # Clear existing text
    adb.run("shell input keyevent KEYCODE_CTRL_LEFT KEYCODE_A")
    time.sleep(0.2)
    
    # Input new text
    adb.run(f"shell input text '{input_value}'")
    
    return True

def scroll_to_element(element_type, text=None, content_desc=None, resource_id=None, direction="down", max_swipes=10, threshold=0.8):
    """
    Scroll until a UI element is found.
    
    Args:
        element_type (str): Type of UI element (button, text_field, checkbox, etc.)
        text (str, optional): Text content to match
        content_desc (str, optional): Content description to match
        resource_id (str, optional): Resource ID to match
        direction (str, optional): Scroll direction (up, down, left, right)
        max_swipes (int, optional): Maximum number of swipe attempts
        threshold (float, optional): Similarity threshold for matching
    
    Returns:
        dict: Found element or None if not found after max_swipes
    """
    adb = get_adb_instance()
    
    # Get screen dimensions
    output = adb.run("shell wm size").strip()
    match = re.search(r'Physical size: (\d+)x(\d+)', output)
    if not match:
        return None
    
    width, height = map(int, match.groups())
    
    # Calculate swipe coordinates based on direction
    if direction == "down":
        start_x, start_y = width // 2, height * 2 // 3
        end_x, end_y = width // 2, height // 3
    elif direction == "up":
        start_x, start_y = width // 2, height // 3
        end_x, end_y = width // 2, height * 2 // 3
    elif direction == "right":
        start_x, start_y = width * 2 // 3, height // 2
        end_x, end_y = width // 3, height // 2
    elif direction == "left":
        start_x, start_y = width // 3, height // 2
        end_x, end_y = width * 2 // 3, height // 2
    else:
        return None
    
    # Try to find the element first without scrolling
    element = find_ui_element(element_type, text, content_desc, resource_id, threshold)
    if element:
        return element
    
    # Scroll and look for the element
    for _ in range(max_swipes):
        adb.run(f"shell input swipe {start_x} {start_y} {end_x} {end_y} 300")
        time.sleep(0.5)
        
        element = find_ui_element(element_type, text, content_desc, resource_id, threshold)
        if element:
            return element
    
    return None

def wait_for_ui_element(element_type, text=None, content_desc=None, resource_id=None, timeout=30, threshold=0.8):
    """
    Wait for a UI element to appear.
    
    Args:
        element_type (str): Type of UI element (button, text_field, checkbox, etc.)
        text (str, optional): Text content to match
        content_desc (str, optional): Content description to match
        resource_id (str, optional): Resource ID to match
        timeout (int, optional): Maximum wait time in seconds
        threshold (float, optional): Similarity threshold for matching
    
    Returns:
        dict: Found element or None if timeout occurs
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        element = find_ui_element(element_type, text, content_desc, resource_id, threshold)
        if element:
            return element
        
        time.sleep(1)
    
    return None

def get_ui_hierarchy_tree():
    """
    Get a hierarchical tree representation of the current UI.
    
    Returns:
        dict: Hierarchical tree of UI elements
    """
    xml_content = get_xml_dump()
    
    try:
        # Simple implementation - in a real scenario, this would use proper XML parsing
        # to build a hierarchical tree
        
        # Extract root node
        root_match = re.search(r'<hierarchy[^>]*>(.*)</hierarchy>', xml_content, re.DOTALL)
        if not root_match:
            return {}
        
        root_content = root_match.group(1)
        
        # Build tree recursively
        return _parse_node(root_content)
    except:
        return {}

def _parse_node(node_content):
    """
    Parse a node and its children recursively.
    
    Args:
        node_content (str): XML content of the node
    
    Returns:
        dict: Node representation with children
    """
    # Extract node attributes
    node_match = re.search(r'<node([^>]*)>(.*)</node>', node_content, re.DOTALL)
    if not node_match:
        return {}
    
    attributes_str = node_match.group(1)
    children_content = node_match.group(2)
    
    # Parse attributes
    node = {}
    for attr in ['resource-id', 'class', 'text', 'content-desc', 'bounds', 'package']:
        attr_match = re.search(f'{attr}="([^"]*)"', attributes_str)
        if attr_match:
            node[attr] = attr_match.group(1)
    
    # Parse children
    node['children'] = []
    
    # Find all child nodes
    child_pattern = r'<node[^>]*>.*?</node>'
    for child_match in re.finditer(child_pattern, children_content, re.DOTALL):
        child_content = child_match.group(0)
        child_node = _parse_node(child_content)
        if child_node:
            node['children'].append(child_node)
    
    return node

def save_ui_hierarchy_to_json(file_path):
    """
    Save the current UI hierarchy to a JSON file.
    
    Args:
        file_path (str): Path to save the JSON file
    
    Returns:
        bool: True if successful, False otherwise
    """
    hierarchy = get_ui_hierarchy_tree()
    
    try:
        with open(file_path, 'w') as f:
            json.dump(hierarchy, f, indent=2)
        return True
    except:
        return False

def find_element_by_xpath(xpath):
    """
    Find an element using XPath-like syntax.
    
    Args:
        xpath (str): XPath-like expression (e.g., "//button[@text='Login']")
    
    Returns:
        dict: Found element or None if not found
    """
    # Parse the XPath expression
    match = re.match(r'//(\w+)(?:\[@([^=]+)=\'([^\']+)\'\])?', xpath)
    if not match:
        return None
    
    element_type, attr_name, attr_value = match.groups()
    
    # Map element type to UI element type
    element_type_map = {
        "button": "button",
        "input": "text_field",
        "checkbox": "checkbox",
        "switch": "switch",
        "radio": "radio_button",
        "select": "spinner",
        "list": "list_view",
        "scroll": "scroll_view",
        "webview": "webview"
    }
    
    ui_element_type = element_type_map.get(element_type.lower(), element_type.lower())
    
    # Map attribute name to criteria
    if attr_name == "text":
        return find_ui_element(ui_element_type, text=attr_value)
    elif attr_name == "content-desc":
        return find_ui_element(ui_element_type, content_desc=attr_value)
    elif attr_name == "resource-id" or attr_name == "id":
        return find_ui_element(ui_element_type, resource_id=attr_value)
    else:
        # For other attributes, try to find by class name directly
        criteria = {"class": attr_value}
        elements = find_elements_by_criteria(criteria)
        return elements[0] if elements else None

def find_all_elements_by_xpath(xpath):
    """
    Find all elements matching an XPath-like expression.
    
    Args:
        xpath (str): XPath-like expression (e.g., "//button[@text='Login']")
    
    Returns:
        list: List of matching elements
    """
    # Parse the XPath expression
    match = re.match(r'//(\w+)(?:\[@([^=]+)=\'([^\']+)\'\])?', xpath)
    if not match:
        return []
    
    element_type, attr_name, attr_value = match.groups()
    
    # Map element type to UI element type
    element_type_map = {
        "button": "button",
        "input": "text_field",
        "checkbox": "checkbox",
        "switch": "switch",
        "radio": "radio_button",
        "select": "spinner",
        "list": "list_view",
        "scroll": "scroll_view",
        "webview": "webview"
    }
    
    ui_element_type = element_type_map.get(element_type.lower(), element_type.lower())
    
    # Map attribute name to criteria
    if attr_name == "text":
        return find_all_ui_elements(ui_element_type, text=attr_value)
    elif attr_name == "content-desc":
        return find_all_ui_elements(ui_element_type, content_desc=attr_value)
    elif attr_name == "resource-id" or attr_name == "id":
        return find_all_ui_elements(ui_element_type, resource_id=attr_value)
    else:
        # For other attributes, try to find by class name directly
        criteria = {"class": attr_value}
        return find_elements_by_criteria(criteria)
