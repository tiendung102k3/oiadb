"""
Các lớp Exception tùy chỉnh cho thư viện My ADB Lib.
"""

class ADBError(Exception):
    """Lớp cơ sở cho tất cả các lỗi liên quan đến ADB."""
    pass


class ADBCommandError(ADBError):
    """Lỗi khi thực thi lệnh ADB không thành công."""
    
    def __init__(self, command, error_message, return_code=None):
        self.command = command
        self.error_message = error_message
        self.return_code = return_code
        message = f"Lỗi khi thực thi lệnh ADB: '{command}'. "
        if return_code is not None:
            message += f"Mã lỗi: {return_code}. "
        message += f"Thông báo lỗi: {error_message}"
        super().__init__(message)


class DeviceNotFoundError(ADBError):
    """Lỗi khi không tìm thấy thiết bị được chỉ định."""
    
    def __init__(self, device_id=None):
        if device_id:
            message = f"Không tìm thấy thiết bị với ID: '{device_id}'"
        else:
            message = "Không tìm thấy thiết bị nào được kết nối"
        super().__init__(message)


class DeviceConnectionError(ADBError):
    """Lỗi khi không thể kết nối đến thiết bị."""
    
    def __init__(self, device_id=None, error_message=None):
        message = "Lỗi kết nối đến thiết bị"
        if device_id:
            message += f" với ID: '{device_id}'"
        if error_message:
            message += f". Chi tiết: {error_message}"
        super().__init__(message)


class PackageNotFoundError(ADBError):
    """Lỗi khi không tìm thấy package được chỉ định."""
    
    def __init__(self, package_name):
        message = f"Không tìm thấy package: '{package_name}'"
        super().__init__(message)


class InstallationError(ADBError):
    """Lỗi khi cài đặt ứng dụng."""
    
    def __init__(self, apk_path, error_message):
        message = f"Lỗi khi cài đặt APK từ '{apk_path}'. Chi tiết: {error_message}"
        super().__init__(message)


class UninstallationError(ADBError):
    """Lỗi khi gỡ cài đặt ứng dụng."""
    
    def __init__(self, package_name, error_message):
        message = f"Lỗi khi gỡ cài đặt package '{package_name}'. Chi tiết: {error_message}"
        super().__init__(message)


class FileOperationError(ADBError):
    """Lỗi khi thực hiện các thao tác với file."""
    
    def __init__(self, operation, source, destination=None, error_message=None):
        message = f"Lỗi khi {operation} '{source}'"
        if destination:
            message += f" đến '{destination}'"
        if error_message:
            message += f". Chi tiết: {error_message}"
        super().__init__(message)


class PermissionError(ADBError):
    """Lỗi khi thao tác với quyền ứng dụng."""
    
    def __init__(self, package_name, permission, error_message=None):
        message = f"Lỗi khi thao tác với quyền '{permission}' cho package '{package_name}'"
        if error_message:
            message += f". Chi tiết: {error_message}"
        super().__init__(message)


class ADBServerError(ADBError):
    """Lỗi liên quan đến máy chủ ADB."""
    
    def __init__(self, error_message=None):
        message = "Lỗi máy chủ ADB"
        if error_message:
            message += f". Chi tiết: {error_message}"
        super().__init__(message)


class TimeoutError(ADBError):
    """Lỗi khi thực thi lệnh vượt quá thời gian chờ."""
    
    def __init__(self, command, timeout):
        message = f"Lệnh '{command}' đã vượt quá thời gian chờ ({timeout} giây)"
        super().__init__(message)
