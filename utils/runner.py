# my_adb_lib/utils/runner.py

import subprocess

def run_adb_command(command, device_id=None):
    """
    Hàm này sẽ thực thi lệnh adb thông qua subprocess.
    """
    if device_id:
        command = f"-s {device_id} {command}"
    
    # Chạy lệnh adb và trả về kết quả
    process = subprocess.Popen(
        ["adb", *command.split()],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    
    if process.returncode != 0:
        return f"Error: {stderr.decode()}"
    
    return stdout.decode()