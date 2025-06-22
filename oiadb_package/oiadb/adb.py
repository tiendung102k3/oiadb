"""
Lớp chính của thư viện My ADB Lib.
"""

import os
import logging
import subprocess
import time
from typing import Optional, List, Dict, Any, Union

from .exceptions import (
    ADBError, ADBCommandError, DeviceNotFoundError, 
    DeviceConnectionError, PackageNotFoundError,
    InstallationError, UninstallationError, FileOperationError
)
from .utils.advanced import CommandResult, ResultCache, DeviceMonitor, AsyncCommandExecutor
from .utils.platform_utils import get_platform_info, ADBInstaller, PlatformInfo

# Thiết lập logging
logger = logging.getLogger("oiadb")

# Constants for the server

class MyADB:
    """
    Lớp chính để tương tác với ADB (Android Debug Bridge).
    
    Attributes:
        device_id (str): ID của thiết bị Android để tương tác
        cache_enabled (bool): Bật/tắt cache kết quả lệnh
        timeout (int): Thời gian chờ tối đa cho các lệnh (giây)
        adb_path (str): Đường dẫn đến executable ADB
        auto_install_adb (bool): Tự động tải xuống và cài đặt ADB nếu không tìm thấy
    """
    
    def __init__(self, device_id: Optional[str] = None, cache_enabled: bool = True, 
                 timeout: int = 30, adb_path: Optional[str] = None,
                 auto_install_adb: bool = True):
        """
        Khởi tạo đối tượng MyADB.
        
        Args:
            device_id: ID của thiết bị Android (serial number)
            cache_enabled: Bật/tắt cache kết quả lệnh
            timeout: Thời gian chờ tối đa cho các lệnh (giây)
            adb_path: Đường dẫn tùy chỉnh đến executable ADB
            auto_install_adb: Tự động tải xuống và cài đặt ADB nếu không tìm thấy
        """
        self.device_id = device_id
        self.timeout = timeout
        self.cache_enabled = cache_enabled
        self.auto_install_adb = auto_install_adb
        
        # Lấy thông tin nền tảng
        self.platform_info = get_platform_info()
        
        # Xác định đường dẫn ADB
        self.adb_path = self._resolve_adb_path(adb_path)
        
        # Khởi tạo cache và executor
        self._cache = ResultCache() if cache_enabled else None
        self._async_executor = AsyncCommandExecutor()
        
        # Kiểm tra ADB đã được cài đặt
        self._check_adb_installed()
        
        # Kiểm tra thiết bị nếu đã chỉ định
        if device_id:
            self._check_device()
        else:
            # Try to get the first device if none specified
            devices = self.get_devices_list()
            if devices:
                self.device_id = devices[0]
                logger.info(f"No device ID specified, using first available device: {self.device_id}")
                self._check_device() # Re-check with the selected device
            else:
                raise DeviceNotFoundError("No devices found connected.")


    def _resolve_adb_path(self, custom_path: Optional[str] = None) -> str:
        """
        Xác định đường dẫn đến ADB, tự động cài đặt nếu cần.
        
        Args:
            custom_path: Đường dẫn tùy chỉnh đến ADB
            
        Returns:
            Đường dẫn đến ADB
            
        Raises:
            ADBError: Nếu không thể tìm thấy hoặc cài đặt ADB
        """
        # Sử dụng đường dẫn tùy chỉnh nếu được cung cấp
        if custom_path:
            if os.path.isfile(custom_path) and os.access(custom_path, os.X_OK):
                logger.debug(f"Using custom ADB path: {custom_path}")
                return custom_path
            else:
                logger.warning(f"Custom ADB path is invalid: {custom_path}")
        
        # Tìm ADB trong hệ thống
        adb_path = self.platform_info.find_adb_path()
        if adb_path:
            logger.debug(f"Found ADB in system: {adb_path}")
            return adb_path
        
        # Tự động cài đặt ADB nếu được bật
        if self.auto_install_adb:
            logger.info("ADB not found in system, attempting to install...")
            installer = ADBInstaller()
            adb_path = installer.install_adb()
            if adb_path:
                logger.info(f"ADB installed successfully: {adb_path}")
                return adb_path
        
        # Sử dụng 'adb' và hy vọng nó có trong PATH
        logger.warning("Could not find or install ADB, falling back to 'adb' command")
        return "adb"
    # --- Existing methods below --- 

    def _check_adb_installed(self) -> None:
        """
        Kiểm tra ADB đã được cài đặt và có thể truy cập.
        
        Raises:
            ADBError: Nếu ADB không được cài đặt hoặc không thể truy cập
        """
        try:
            # Sử dụng platform_utils để tạo đối số phù hợp với nền tảng
            process_args = self.platform_info.create_process_args(
                [self.adb_path, "version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self.timeout
            )
            
            result = subprocess.run(**process_args)
            stdout_str = result.stdout.decode(errors='ignore')
            stderr_str = result.stderr.decode(errors='ignore')
            
            if result.returncode != 0:
                raise ADBError(f"Không thể chạy ADB. Lỗi: {stderr_str}")
            logger.debug(f"ADB version: {stdout_str.splitlines()[0]}")
        except FileNotFoundError:
            raise ADBError("ADB không được cài đặt hoặc không có trong PATH")
        except Exception as e:
            raise ADBError(f"Lỗi khi kiểm tra ADB: {str(e)}")
    
    def _check_device(self) -> None:
        """
        Kiểm tra thiết bị đã được kết nối.
        
        Raises:
            DeviceNotFoundError: Nếu thiết bị không được tìm thấy
        """
        devices = self.get_devices_list()
        if self.device_id not in devices:
            raise DeviceNotFoundError(self.device_id)
    
    def run(self, command: str, use_cache: bool = True) -> str:
        """
        Chạy lệnh ADB và trả về kết quả dưới dạng chuỗi.
        
        Args:
            command: Lệnh ADB cần thực thi (không bao gồm "adb")
            use_cache: Có sử dụng cache hay không
            
        Returns:
            Kết quả lệnh dưới dạng chuỗi
            
        Raises:
            ADBCommandError: Nếu lệnh thất bại
        """
        # Kiểm tra cache
        cache_key = f"{self.device_id}:{command}" if self.device_id else command
        if self.cache_enabled and use_cache and self._cache:
            cached_result = self._cache.get(cache_key)
            if cached_result:
                logger.debug(f"Using cached result for command: {command}")
                return cached_result
        
        # Tạo lệnh đầy đủ
        full_command = [self.adb_path]
        if self.device_id:
            full_command.extend(["-s", self.device_id])
        full_command.extend(command.split())
        
        # Thực thi lệnh
        try:
            logger.debug("Executing command: {}".format(" ".join(full_command)))
            
            # Sử dụng platform_utils để tạo đối số phù hợp với nền tảng
            process_args = self.platform_info.create_process_args(
                full_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self.timeout,
                check=False # Don't raise CalledProcessError automatically
            )
            
            result = subprocess.run(**process_args)
            stdout_str = result.stdout.decode(errors='ignore')
            stderr_str = result.stderr.decode(errors='ignore')
            
            if result.returncode != 0:
                # Handle specific known non-fatal errors if necessary
                # Example: adb forward --remove error when forward doesn't exist
                if "cannot remove listener" in stderr_str and "forward --remove" in command:
                    logger.debug(f"Ignoring error for 'forward --remove': {stderr_str.strip()}")
                    return stdout_str # Return stdout even if stderr had this specific error
                
                raise ADBCommandError(
                    command=" ".join(full_command),
                    error_message=stderr_str,
                    return_code=result.returncode
                )
            
            # Lưu vào cache nếu thành công
            if self.cache_enabled and use_cache and self._cache:
                self._cache.set(cache_key, stdout_str)
            
            return stdout_str
        
        except subprocess.TimeoutExpired:
            raise ADBCommandError(
                command=" ".join(full_command),
                error_message=f"Command timed out after {self.timeout} seconds",
                return_code=-1
            )
        except Exception as e:
            raise ADBCommandError(
                command=" ".join(full_command),
                error_message=str(e),
                return_code=-1
            )
    
    def run_async(self, command: str, callback=None) -> str:
        """
        Chạy lệnh ADB bất đồng bộ.
        
        Args:
            command: Lệnh ADB cần thực thi (không bao gồm "adb")
            callback: Hàm callback khi lệnh hoàn thành
            
        Returns:
            ID của lệnh bất đồng bộ
        """
        # Tạo ID duy nhất cho lệnh
        import uuid
        command_id = str(uuid.uuid4())
        
        # Tạo lệnh đầy đủ
        full_command = [self.adb_path]
        if self.device_id:
            full_command.extend(["-s", self.device_id])
        full_command.extend(command.split())
        
        # Thực thi lệnh bất đồng bộ
        self._async_executor.execute(
            command_id=command_id,
            command=full_command,
            callback=callback,
            timeout=self.timeout
        )
        
        return command_id
    
    def get_async_result(self, command_id: str) -> Optional[CommandResult]:
        """
        Lấy kết quả của lệnh bất đồng bộ.
        
        Args:
            command_id: ID của lệnh
            
        Returns:
            CommandResult hoặc None nếu lệnh chưa hoàn thành
        """
        return self._async_executor.get_result(command_id)
    
    def is_async_running(self, command_id: str) -> bool:
        """
        Kiểm tra xem lệnh bất đồng bộ có đang chạy không.
        
        Args:
            command_id: ID của lệnh
            
        Returns:
            True nếu lệnh đang chạy, False nếu không
        """
        return self._async_executor.is_running(command_id)
    
    def kill_async(self, command_id: str) -> bool:
        """
        Hủy lệnh bất đồng bộ đang chạy.
        
        Args:
            command_id: ID của lệnh
            
        Returns:
            True nếu lệnh đã bị hủy thành công, False nếu không
        """
        return self._async_executor.kill(command_id)
    
    def clear_cache(self) -> None:
        """Xóa toàn bộ cache."""
        if self.cache_enabled and self._cache:
            self._cache.clear()
    
    def get_devices(self) -> str:
        """
        Liệt kê các thiết bị kết nối dưới dạng chuỗi.
        
        Returns:
            Chuỗi chứa danh sách thiết bị
        """
        return self.run("devices", use_cache=False)
    
    def get_devices_list(self) -> List[str]:
        """
        Liệt kê các thiết bị kết nối dưới dạng danh sách.
        
        Returns:
            Danh sách các ID thiết bị
        """
        output = self.get_devices()
        devices = []
        
        for line in output.splitlines()[1:]:  # Bỏ qua dòng tiêu đề
            if not line.strip():
                continue
            
            parts = line.split("\t")
            if len(parts) >= 2 and parts[1] == "device":
                devices.append(parts[0])
        
        return devices
    
    def reboot_device(self) -> str:
        """
        Khởi động lại thiết bị.
        
        Returns:
            Kết quả lệnh
        """
        return self.run("reboot")
    
    def reboot_to_recovery(self) -> str:
        """
        Khởi động lại thiết bị vào chế độ recovery.
        
        Returns:
            Kết quả lệnh
        """
        return self.run("reboot recovery")
    
    def reboot_to_bootloader(self) -> str:
        """
        Khởi động lại thiết bị vào chế độ bootloader.
        
        Returns:
            Kết quả lệnh
        """
        return self.run("reboot bootloader")
    
    def install_app(self, apk_path: str, replace: bool = False, 
                   grant_permissions: bool = False) -> str:
        """
        Cài đặt ứng dụng từ đường dẫn .apk.
        
        Args:
            apk_path: Đường dẫn đến file APK
            replace: Thay thế ứng dụng nếu đã tồn tại
            grant_permissions: Tự động cấp tất cả quyền cho ứng dụng
            
        Returns:
            Kết quả lệnh
            
        Raises:
            InstallationError: Nếu cài đặt thất bại
        """
        # Chuẩn hóa đường dẫn
        apk_path = self.platform_info.normalize_path(apk_path)
        
        if not os.path.exists(apk_path):
            raise InstallationError(apk_path, "File APK không tồn tại")
        
        options = []
        if replace:
            options.append("-r")
        if grant_permissions:
            options.append("-g")
        
        try:
            # Add -t flag if installing test APKs might be needed, though server is not test-only
            return self.run("install {} {}".format(" ".join(options), apk_path))
        except ADBCommandError as e:
            raise InstallationError(apk_path, e.error_message)
    
    def uninstall_app(self, package_name: str, keep_data: bool = False) -> str:
        """
        Gỡ cài đặt ứng dụng theo tên package.
        
        Args:
            package_name: Tên package của ứng dụng
            keep_data: Giữ lại dữ liệu và cache
            
        Returns:
            Kết quả lệnh
            
        Raises:
            UninstallationError: Nếu gỡ cài đặt thất bại
        """
        options = ["-k"] if keep_data else []
        
        try:
            return self.run("uninstall {} {}".format(" ".join(options), package_name))
        except ADBCommandError as e:
            # Check if uninstall failed because package doesn't exist
            if "not found" in e.error_message.lower():
                 logger.warning("Attempted to uninstall non-existent package: {}".format(package_name))
                 return "Package not found"
            raise UninstallationError(package_name, e.error_message)
    
    def push_file(self, local_path: str, remote_path: str) -> str:
        """
        Đẩy file từ máy tính vào thiết bị.
        
        Args:
            local_path: Đường dẫn file trên máy tính
            remote_path: Đường dẫn đích trên thiết bị
            
        Returns:
            Kết quả lệnh
            
        Raises:
            FileOperationError: Nếu thao tác thất bại
        """
        # Chuẩn hóa đường dẫn local
        local_path = self.platform_info.normalize_path(local_path)
        
        if not os.path.exists(local_path):
            raise FileOperationError("push", local_path, remote_path, "File nguồn không tồn tại")
        
        try:
            return self.run(f"push \"{local_path}\" \"{remote_path}\"")
        except ADBCommandError as e:
            raise FileOperationError("push", local_path, remote_path, e.error_message)
    
    def pull_file(self, remote_path: str, local_path: str) -> str:
        """
        Lấy file từ thiết bị về máy tính.
        
        Args:
            remote_path: Đường dẫn file trên thiết bị
            local_path: Đường dẫn đích trên máy tính
            
        Returns:
            Kết quả lệnh
            
        Raises:
            FileOperationError: Nếu thao tác thất bại
        """
        # Chuẩn hóa đường dẫn local
        local_path = self.platform_info.normalize_path(local_path)
        
        # Đảm bảo thư mục cha tồn tại
        os.makedirs(os.path.dirname(os.path.abspath(local_path)), exist_ok=True)
        
        try:
            return self.run(f"pull \"{remote_path}\" \"{local_path}\"")
        except ADBCommandError as e:
            raise FileOperationError("pull", remote_path, local_path, e.error_message)
    
    def get_device_info(self) -> Dict[str, str]:
        """
        Lấy thông tin thiết bị.
        
        Returns:
            Dictionary chứa thông tin thiết bị
        """
        try:
            # Use server RPC call if available for potentially richer info
            # Example: info = self._server_rpc_call("deviceInfo")
            # Fallback to getprop for now
            output = self.run("shell getprop")
            properties = {}
            
            for line in output.splitlines():
                line = line.strip()
                if not line or ": " not in line:
                    continue
                
                # Handle format like [ro.product.brand]: [google]
                if line.startswith("[") and "]: [" in line:
                    key_part, value_part = line.split("]: [", 1)
                    key = key_part[1:]
                    value = value_part[:-1]
                    properties[key] = value
                # Handle simpler format if needed (though getprop usually uses the above)
                # elif ": " in line:
                #     key, value = line.split(": ", 1)
                #     properties[key] = value

            return properties
        except ADBCommandError as e:
            logger.error(f"Error getting device info: {e}")
            return {}
    
    def start_app(self, package_name: str, activity: Optional[str] = None) -> str:
        """
        Khởi động ứng dụng.
        
        Args:
            package_name: Tên package của ứng dụng
            activity: Tên activity để khởi động (tùy chọn)
            
        Returns:
            Kết quả lệnh
        """
        # Consider using server's open.app method if available
        if activity:
            # Ensure activity name doesn't start with . if package is included
            if activity.startswith("."):
                 full_activity = package_name + activity
            else:
                 full_activity = activity # Assume full name provided
            return self.run(f"shell am start -n {package_name}/{full_activity}")
        else:
            # Use monkey for finding launcher activity (less reliable than server method)
            return self.run(f"shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
    
    def stop_app(self, package_name: str) -> str:
        """
        Dừng ứng dụng.
        
        Args:
            package_name: Tên package của ứng dụng
            
        Returns:
            Kết quả lệnh
        """
        # Server might offer a more graceful stop?
        return self.run(f"shell am force-stop {package_name}")
    
    def clear_app_data(self, package_name: str) -> str:
        """
        Xóa dữ liệu ứng dụng.
        
        Args:
            package_name: Tên package của ứng dụng
            
        Returns:
            Kết quả lệnh
        """
        return self.run(f"shell pm clear {package_name}")
    
    def get_app_version(self, package_name: str) -> Optional[str]:
        """
        Lấy phiên bản của ứng dụng.
        
        Args:
            package_name: Tên package của ứng dụng
            
        Returns:
            Phiên bản ứng dụng (versionName) or None if not found.
            
        Raises:
            PackageNotFoundError: If dumpsys command fails significantly.
        """
        try:
            output = self.run(f"shell dumpsys package {package_name}")
            for line in output.splitlines():
                line = line.strip()
                if line.startswith("versionName="):
                    return line.split("=", 1)[1].strip()
            
            # If loop finishes without finding versionName, package might exist but lack info
            # Check if package exists at all
            if not self.is_app_installed(package_name):
                 raise PackageNotFoundError(package_name)
            return None # Package exists, but versionName not found in dumpsys
        except ADBCommandError as e:
            # If dumpsys fails entirely, treat as package not found or inaccessible
            logger.warning(f"dumpsys package {package_name} failed: {e}")
            raise PackageNotFoundError(package_name)
    
    def is_app_installed(self, package_name: str) -> bool:
        """
        Kiểm tra xem ứng dụng đã được cài đặt chưa.
        
        Args:
            package_name: Tên package của ứng dụng
            
        Returns:
            True nếu ứng dụng đã được cài đặt, False nếu không
        """
        try:
            # pm list packages returns 'package:<n>'
            output = self.run(f"shell pm list packages {package_name}")
            return f"package:{package_name}" in output
        except ADBCommandError:
            return False
    
    def take_screenshot(self, output_path: Optional[str] = None, 
                       as_bytes: bool = False) -> Union[str, bytes, None]:
        """
        Chụp ảnh màn hình thiết bị.
        
        Args:
            output_path: Đường dẫn lưu ảnh (tùy chọn)
            as_bytes: Trả về dữ liệu ảnh dưới dạng bytes thay vì lưu file
            
        Returns:
            - Nếu output_path được cung cấp: Đường dẫn đến file ảnh đã lưu
            - Nếu as_bytes=True: Dữ liệu ảnh dưới dạng bytes
            - Nếu cả hai: None
            
        Raises:
            ADBCommandError: Nếu lệnh thất bại
            FileOperationError: Nếu không thể lưu file
        """
        # Sử dụng đường dẫn tạm thời phù hợp với thiết bị
        device_temp_dir = self.platform_info.get_device_temp_dir()
        remote_path = f"{device_temp_dir}/screenshot_oiadb.png"
        
        try:
            # Chụp ảnh màn hình
            self.run(f"shell screencap -p {remote_path}")
            
            if as_bytes:
                # Lấy dữ liệu ảnh dưới dạng bytes
                output = self.run(f"exec-out cat {remote_path}")
                # Xóa file tạm trên thiết bị
                self.run(f"shell rm {remote_path}")
                return output.encode('latin-1')  # Convert to bytes
            
            if output_path:
                # Chuẩn hóa đường dẫn output
                output_path = self.platform_info.normalize_path(output_path)
                
                # Đảm bảo thư mục cha tồn tại
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                
                # Lấy ảnh về máy tính
                self.pull_file(remote_path, output_path)
                # Xóa file tạm trên thiết bị
                self.run(f"shell rm {remote_path}")
                return output_path
            
            # Nếu không cần lưu file hoặc trả về bytes, xóa file tạm
            self.run(f"shell rm {remote_path}")
            return None
        
        except (ADBCommandError, FileOperationError) as e:
            logger.error(f"Screenshot failed: {e}")
            # Cố gắng xóa file tạm nếu có lỗi
            try:
                self.run(f"shell rm {remote_path}")
            except ADBCommandError:
                pass  # Bỏ qua lỗi khi xóa file tạm
            raise

    def record_screen(self, output_path: str, time_limit: int = 180, 
                     size: Optional[str] = None, bit_rate: Optional[int] = None) -> str:
        """
        Quay video màn hình thiết bị.
        
        Args:
            output_path: Đường dẫn lưu video (local path)
            time_limit: Giới hạn thời gian quay (giây), max 180
            size: Kích thước video (ví dụ: "1280x720")
            bit_rate: Bit rate (ví dụ: 4000000 cho 4Mbps)
            
        Returns:
            Message indicating success or failure.
            
        Raises:
            FileOperationError: If pulling the file fails.
            ADBCommandError: If screenrecord command fails.
        """
        # Chuẩn hóa đường dẫn output
        output_path = self.platform_info.normalize_path(output_path)
        
        # Đảm bảo thư mục cha tồn tại
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Sử dụng đường dẫn tạm thời phù hợp với thiết bị
        device_temp_dir = self.platform_info.get_device_temp_dir()
        remote_path = f"{device_temp_dir}/screenrecord_oiadb.mp4"
        
        time_limit = min(time_limit, 180) # Enforce max time limit for screenrecord
        
        command = f"shell screenrecord"
        if time_limit:
            command += f" --time-limit {time_limit}"
        if size:
            command += f" --size {size}"
        if bit_rate:
            command += f" --bit-rate {bit_rate}"
        command += f" {remote_path}"
        
        try:
            logger.info(f"Starting screen recording (max {time_limit}s)... Output: {output_path}")
            # Run screenrecord and wait for it to finish (up to time_limit + buffer)
            self.run(command, use_cache=False) # Timeout handled by self.run
            
            logger.info("Screen recording finished. Pulling file...")
            self.pull_file(remote_path, output_path)
            
            # Clean up remote file
            self.run(f"shell rm {remote_path}", use_cache=False)
            
            return f"Screen recording saved to {output_path}"
        except (ADBCommandError, FileOperationError) as e:
            logger.error(f"Screen recording failed: {e}")
            # Attempt cleanup even if recording/pulling failed
            try:
                self.run(f"shell rm {remote_path}", use_cache=False)
            except ADBCommandError:
                pass # Ignore cleanup error
            raise # Re-raise the original error

    def input_keyevent(self, keycode: Union[int, str]) -> str:
        """
        Gửi sự kiện nhấn phím.
        
        Args:
            keycode: Mã phím (ví dụ: 3 cho HOME, 4 cho BACK, "KEYCODE_HOME")
            
        Returns:
            Kết quả lệnh
        """
        # Consider using server's press method
        return self.run(f"shell input keyevent {keycode}")

    def input_text(self, text: str) -> str:
        """
        Nhập văn bản.
        
        Args:
            text: Văn bản cần nhập
            
        Returns:
            Kết quả lệnh
        """
        # Consider using server's input method (handles unicode better)
        # Escape special characters for shell input
        escaped_text = text.replace(" ", "%s").replace("\"", "\\\"").replace("(", "\\(").replace(")", "\\)").replace("<", "\\<").replace(">", "\\>").replace("{", "\\{").replace("}", "\\}").replace("&", "\\&").replace(";", "\\;").replace("|", "\\|").replace("$", "\\$").replace("`", "\\`")
        return self.run(f"shell input text \"{escaped_text}\"")

    def input_tap(self, x: int, y: int) -> str:
        """
        Chạm vào tọa độ màn hình.
        
        Args:
            x: Tọa độ X
            y: Tọa độ Y
            
        Returns:
            Kết quả lệnh
        """
        # Consider using server's click method
        return self.run(f"shell input tap {x} {y}")

    def input_swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> str:
        """
        Vuốt màn hình từ điểm (x1, y1) đến (x2, y2).
        
        Args:
            x1, y1: Tọa độ bắt đầu
            x2, y2: Tọa độ kết thúc
            duration: Thời gian vuốt (ms)
            
        Returns:
            Kết quả lệnh
        """
        # Consider using server's swipe method
        return self.run(f"shell input swipe {x1} {y1} {x2} {y2} {duration}")

    def get_screen_size(self) -> Optional[Dict[str, int]]:
        """
        Lấy kích thước màn hình (width, height).
        
        Returns:
            Dictionary {"width": w, "height": h} hoặc None nếu lỗi.
        """
        try:
            # Try server method first
            info = self._server_rpc_call("deviceInfo")
            if info and "displayWidth" in info and "displayHeight" in info:
                return {"width": info["displayWidth"], "height": info["displayHeight"]}
        except (ADBError, ADBCommandError) as e:
            logger.warning(f"RPC get screen size failed: {e}. Falling back to ADB.")
        
        # Fallback to ADB
        try:
            output = self.run("shell wm size")
            # Output: Physical size: 1080x1920 or Override size: 1080x1920
            size_line = output.splitlines()[-1] # Get the last line
            if ":" in size_line:
                size_str = size_line.split(":")[1].strip()
                width, height = map(int, size_str.split("x"))
                return {"width": width, "height": height}
            return None
        except (ADBCommandError, ValueError) as e:
            logger.error(f"Failed to get screen size: {e}")
            return None
    
    def _server_rpc_call(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Gọi phương thức RPC trên server.
        
        Args:
            method: Tên phương thức
            params: Tham số (tùy chọn)
            
        Returns:
            Kết quả từ server
            
        Raises:
            ADBError: Nếu không thể kết nối đến server
        """
        if not self.local_server_port:
            raise ADBError("Server not connected. Call setup_server() first.")
        
        import json
        
        url = f"http://127.0.0.1:{self.local_server_port}/{method}"
        params_dict = params or {}
        
        try:
            response = requests.post(url, json=params_dict, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ADBError(f"RPC call failed: {e}")
        except json.JSONDecodeError:
            raise ADBError("Invalid JSON response from server")
