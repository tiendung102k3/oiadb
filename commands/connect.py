from .core import run_command

def connect_default(ip, port):
    """
    Kết nối ADB qua IP và port mặc định (192.168.0.1:5555)
    """
    return run_command(f"adb connect {ip}:{port}")

def connect_pair(ip, port, pairing_code):
    """
    Kết nối ADB qua IP, port và mã ghép nối.
    """
    pairing_command = f"adb pair {ip}:{port} {pairing_code}"
    result = run_command(pairing_command)
    
    return result