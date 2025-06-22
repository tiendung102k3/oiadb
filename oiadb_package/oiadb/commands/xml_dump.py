"""
Module for obtaining UI hierarchy XML dump using ADB.
"""

import re
import logging
import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..adb import MyADB # Use type checking import to avoid circular dependency issues

logger = logging.getLogger("oiadb")

def get_ui_xml_dump(adb: "MyADB") -> str:
    """
    Get XML dump of the current UI hierarchy using standard ADB commands.

    Args:
        adb: An instance of the MyADB class.

    Returns:
        str: XML representation of the UI hierarchy, or empty string if failed.
    """
    xml_content = ""
    error_message = ""

    # Method 1: Direct dump to stdout (fastest, works on most devices)
    try:
        # Use a specific timeout for this potentially long-running command
        # Use run method from the passed adb instance
        xml_output = adb.run("shell uiautomator dump /dev/tty", use_cache=False)
        # Check if the output contains valid XML hierarchy
        if "<hierarchy" in xml_output and "</hierarchy>" in xml_output:
            # Extract XML content between hierarchy tags more reliably
            match = re.search(r"(<\?xml.*?<hierarchy.*?<\/hierarchy>)", xml_output, re.DOTALL)
            if match:
                xml_content = match.group(1)
                logger.debug("Successfully obtained XML dump via /dev/tty")
                return xml_content
            else:
                # Sometimes the output might be truncated or malformed
                logger.warning("Could not extract hierarchy from /dev/tty output.")
        else:
            # Handle cases where dump command fails or returns non-XML output
            logger.warning("uiautomator dump /dev/tty did not return valid XML hierarchy.")
            if "ERROR:" in xml_output or "java.lang.Exception" in xml_output:
                 error_message = xml_output # Store potential error message

    except Exception as e:
        logger.warning("Failed to get XML dump via /dev/tty: %s", e)
        error_message = str(e)

    # Method 2: Standard dump to file then read (fallback)
    logger.debug("Falling back to XML dump via file method.")
    try:
        # Define a temporary file path on the device
        remote_xml_path = "/data/local/tmp/oiadb_uidump.xml"
        # Run the dump command saving to the temporary file
        dump_result = adb.run(f"shell uiautomator dump {remote_xml_path}", use_cache=False)
        logger.debug("Dump to file result: %s", dump_result)

        # Check if dump command indicated success (might vary)
        # A simple check is just to try reading the file
        try:
            # Read the content of the dumped XML file
            xml_content = adb.run(f"shell cat {remote_xml_path}", use_cache=False)
            # Clean up the temporary file on the device
            adb.run(f"shell rm {remote_xml_path}", use_cache=False)

            # Basic validation
            if "<hierarchy" in xml_content and "</hierarchy>" in xml_content:
                logger.debug("Successfully obtained XML dump via file method.")
                return xml_content
            else:
                logger.warning("Content read from %s does not appear to be valid XML hierarchy.", remote_xml_path)
                xml_content = "" # Reset content if invalid
                if not error_message: # Store error if not already set
                    error_message = "Invalid content from dump file."

        except Exception as read_err:
            logger.warning("Failed to read or delete XML dump file %s: %s", remote_xml_path, read_err)
            if not error_message:
                 error_message = str(read_err)

    except Exception as e:
        logger.error("Failed to get XML dump via file method: %s", e)
        if not error_message:
             error_message = str(e)

    # If both methods failed, log the last known error
    if not xml_content:
        logger.error("Failed to obtain UI XML dump using all methods. Last error: %s", error_message)

    return xml_content

# --- Removed server, filtering, and other API-related functions --- 
# --- Kept similarity_score as it might be useful for future filtering logic --- 

from difflib import SequenceMatcher
from functools import lru_cache

@lru_cache(maxsize=1024)
def similarity_score(str1, str2):
    """
    Calculate similarity score between two strings using efficient algorithm.
    Cached for performance.

    Args:
        str1 (str): First string
        str2 (str): Second string

    Returns:
        float: Similarity score between 0 and 1
    """
    if not str1 and not str2:
        return 1.0  # Both strings are empty

    if not str1 or not str2:
        return 0.0  # One string is empty

    # Convert to lowercase for case-insensitive comparison
    str1 = str1.lower()
    str2 = str2.lower()

    # Quick check for exact match
    if str1 == str2:
        return 1.0

    # Check if one string contains the other
    if str1 in str2 or str2 in str1:
        return 0.9  # High similarity but not perfect

    # Use SequenceMatcher for more accurate similarity
    return SequenceMatcher(None, str1, str2).ratio()

