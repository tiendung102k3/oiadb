"""
Các lệnh quản lý thiết bị Android.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple

from ..exceptions import ADBCommandError

logger = logging.getLogger('my_adb_lib')

class DeviceCommands:
    """
    Lớp chứa các lệnh quản lý thiết bị Android.
    """
    
    def __init__(self, adb_runner):
        """
        Khởi tạo đối tượng DeviceCommands.
        
        Args:
            adb_runner: Đối tượng thực thi lệnh ADB
        """
        self.adb = adb_runner
    
    def get_state(self) -> str:
        """
        Lấy trạng thái thiết bị.
        
        Returns:
            Trạng thái thiết bị (device, offline, unknown)
        """
        logger.debug("Getting device state")
        return self.adb.run("get-state")
    
    def get_serialno(self) -> str:
        """
        Lấy số serial của thiết bị.
        
        Returns:
            Số serial của thiết bị
        """
        logger.debug("Getting device serial number")
        return self.adb.run("get-serialno")
    
    def get_imei(self) -> str:
        """
        Lấy IMEI của thiết bị.
        
        Returns:
            IMEI của thiết bị
        """
        logger.debug("Getting device IMEI")
        return self.adb.run("shell dumpsys iphonesybinfo")
    
    def battery(self) -> Dict[str, Any]:
        """
        Lấy thông tin pin.
        
        Returns:
            Dictionary chứa thông tin pin
        """
        try:
            logger.debug("Getting battery information")
            output = self.adb.run("shell dumpsys battery")
            battery_info = {}
            
            for line in output.splitlines():
                line = line.strip()
                if not line or ': ' not in line:
                    continue
                
                key, value = line.split(': ', 1)
                try:
                    # Thử chuyển đổi giá trị thành số
                    value = int(value) if value.isdigit() else float(value) if '.' in value and value.replace('.', '').isdigit() else value
                except:
                    pass
                
                battery_info[key] = value
            
            return battery_info
        except ADBCommandError as e:
            logger.error(f"Error getting battery info: {e}")
            return {}
    
    def current_dir(self) -> str:
        """
        Lấy thư mục hiện tại trên thiết bị.
        
        Returns:
            Đường dẫn thư mục hiện tại
        """
        logger.debug("Getting current directory")
        return self.adb.run("shell pwd")
    
    def list_features(self) -> List[str]:
        """
        Liệt kê các tính năng của thiết bị.
        
        Returns:
            Danh sách các tính năng
        """
        try:
            logger.debug("Listing device features")
            output = self.adb.run("shell pm list features")
            features = []
            
            for line in output.splitlines():
                if line.startswith("feature:"):
                    features.append(line[8:])
            
            return features
        except ADBCommandError as e:
            logger.error(f"Error listing features: {e}")
            return []
    
    def service_list(self) -> List[str]:
        """
        Liệt kê các dịch vụ đang chạy.
        
        Returns:
            Danh sách các dịch vụ
        """
        try:
            logger.debug("Listing services")
            output = self.adb.run("shell service list")
            services = []
            
            for line in output.splitlines():
                if line and ":" in line:
                    services.append(line.strip())
            
            return services
        except ADBCommandError as e:
            logger.error(f"Error listing services: {e}")
            return []
    
    def screen_size(self) -> Tuple[int, int]:
        """
        Lấy kích thước màn hình.
        
        Returns:
            Tuple (width, height) chứa kích thước màn hình
        """
        try:
            logger.debug("Getting screen size")
            output = self.adb.run("shell wm size")
            for line in output.splitlines():
                if "Physical size" in line:
                    size = line.split(": ")[1]
                    width, height = map(int, size.split("x"))
                    return (width, height)
            
            return (0, 0)
        except Exception as e:
            logger.error(f"Error getting screen size: {e}")
            return (0, 0)
    
    def screen_density(self) -> int:
        """
        Lấy mật độ điểm ảnh của màn hình.
        
        Returns:
            Mật độ điểm ảnh (dpi)
        """
        try:
            logger.debug("Getting screen density")
            output = self.adb.run("shell wm density")
            for line in output.splitlines():
                if "Physical density" in line:
                    density = line.split(": ")[1]
                    return int(density)
            
            return 0
        except Exception as e:
            logger.error(f"Error getting screen density: {e}")
            return 0
    
    def get_android_version(self) -> str:
        """
        Lấy phiên bản Android.
        
        Returns:
            Phiên bản Android
        """
        try:
            logger.debug("Getting Android version")
            output = self.adb.run("shell getprop ro.build.version.release")
            return output.strip()
        except ADBCommandError as e:
            logger.error(f"Error getting Android version: {e}")
            return ""
    
    def get_sdk_version(self) -> int:
        """
        Lấy phiên bản SDK.
        
        Returns:
            Phiên bản SDK
        """
        try:
            logger.debug("Getting SDK version")
            output = self.adb.run("shell getprop ro.build.version.sdk")
            return int(output.strip())
        except (ADBCommandError, ValueError) as e:
            logger.error(f"Error getting SDK version: {e}")
            return 0
    
    def get_device_model(self) -> str:
        """
        Lấy model thiết bị.
        
        Returns:
            Model thiết bị
        """
        try:
            logger.debug("Getting device model")
            output = self.adb.run("shell getprop ro.product.model")
            return output.strip()
        except ADBCommandError as e:
            logger.error(f"Error getting device model: {e}")
            return ""
    
    def get_device_manufacturer(self) -> str:
        """
        Lấy nhà sản xuất thiết bị.
        
        Returns:
            Nhà sản xuất thiết bị
        """
        try:
            logger.debug("Getting device manufacturer")
            output = self.adb.run("shell getprop ro.product.manufacturer")
            return output.strip()
        except ADBCommandError as e:
            logger.error(f"Error getting device manufacturer: {e}")
            return ""
    
    def get_device_info(self) -> Dict[str, Any]:
        """
        Lấy thông tin chi tiết về thiết bị.
        
        Returns:
            Dictionary chứa thông tin thiết bị
        """
        try:
            logger.debug("Getting device information")
            info = {
                "android_version": self.get_android_version(),
                "sdk_version": self.get_sdk_version(),
                "model": self.get_device_model(),
                "manufacturer": self.get_device_manufacturer(),
                "serial": self.get_serialno(),
                "screen_size": self.screen_size(),
                "screen_density": self.screen_density(),
                "battery": self.battery()
            }
            
            # Thêm thông tin từ getprop
            output = self.adb.run("shell getprop")
            for line in output.splitlines():
                line = line.strip()
                if not line or ': ' not in line:
                    continue
                
                key, value = line.split(': ', 1)
                key = key.strip('[]')
                value = value.strip('[]')
                
                # Chỉ thêm các thông tin quan trọng
                if any(k in key for k in ['product', 'build', 'version', 'model', 'brand', 'device']):
                    info[key] = value
            
            return info
        except ADBCommandError as e:
            logger.error(f"Error getting device info: {e}")
            return {}
    
    def reboot(self, mode: Optional[str] = None) -> str:
        """
        Khởi động lại thiết bị.
        
        Args:
            mode: Chế độ khởi động lại (None, 'recovery', 'bootloader', 'fastboot')
            
        Returns:
            Kết quả lệnh
        """
        if mode:
            logger.debug(f"Rebooting device to {mode}")
            return self.adb.run(f"reboot {mode}")
        else:
            logger.debug("Rebooting device")
            return self.adb.run("reboot")
    
    def reboot_recovery(self) -> str:
        """
        Khởi động lại thiết bị vào chế độ recovery.
        
        Returns:
            Kết quả lệnh
        """
        return self.reboot("recovery")
    
    def reboot_bootloader(self) -> str:
        """
        Khởi động lại thiết bị vào chế độ bootloader.
        
        Returns:
            Kết quả lệnh
        """
        return self.reboot("bootloader")
    
    def reboot_fastboot(self) -> str:
        """
        Khởi động lại thiết bị vào chế độ fastboot.
        
        Returns:
            Kết quả lệnh
        """
        return self.reboot("fastboot")
    
    def screencap(self, remote_path: str) -> str:
        """
        Chụp ảnh màn hình thiết bị.
        
        Args:
            remote_path: Đường dẫn lưu ảnh trên thiết bị
            
        Returns:
            Kết quả lệnh
        """
        logger.debug(f"Taking screenshot to {remote_path}")
        return self.adb.run(f"shell screencap -p {remote_path}")
    
    def take_screenshot(self, local_path: str) -> str:
        """
        Chụp ảnh màn hình và lưu vào máy tính.
        
        Args:
            local_path: Đường dẫn lưu ảnh trên máy tính
            
        Returns:
            Kết quả lệnh
        """
        logger.debug(f"Taking screenshot to local path {local_path}")
        remote_path = "/sdcard/screenshot.png"
        self.screencap(remote_path)
        result = self.adb.run(f"pull {remote_path} {local_path}")
        self.adb.run(f"shell rm {remote_path}")
        return result
    
    def screenrecord(self, remote_path: str, time_limit: int = 180, 
                    size: Optional[str] = None, bit_rate: Optional[int] = None) -> str:
        """
        Quay video màn hình thiết bị.
        
        Args:
            remote_path: Đường dẫn lưu video trên thiết bị
            time_limit: Giới hạn thời gian quay (giây)
            size: Kích thước video (ví dụ: "1280x720")
            bit_rate: Bit rate (ví dụ: 4000000 cho 4Mbps)
            
        Returns:
            Kết quả lệnh
        """
        cmd = f"shell screenrecord"
        if time_limit:
            cmd += f" --time-limit {time_limit}"
        if size:
            cmd += f" --size {size}"
        if bit_rate:
            cmd += f" --bit-rate {bit_rate}"
        cmd += f" {remote_path}"
        
        logger.debug(f"Recording screen to {remote_path}")
        return self.adb.run(cmd)
    
    def record_screen(self, local_path: str, time_limit: int = 180, 
                     size: Optional[str] = None, bit_rate: Optional[int] = None) -> str:
        """
        Quay video màn hình và lưu vào máy tính.
        
        Args:
            local_path: Đường dẫn lưu video trên máy tính
            time_limit: Giới hạn thời gian quay (giây)
            size: Kích thước video (ví dụ: "1280x720")
            bit_rate: Bit rate (ví dụ: 4000000 cho 4Mbps)
            
        Returns:
            ID của lệnh đang chạy
        """
        logger.debug(f"Recording screen to local path {local_path}")
        remote_path = "/sdcard/screenrecord.mp4"
        
        cmd = f"shell screenrecord"
        if time_limit:
            cmd += f" --time-limit {time_limit}"
        if size:
            cmd += f" --size {size}"
        if bit_rate:
            cmd += f" --bit-rate {bit_rate}"
        cmd += f" {remote_path}"
        
        def callback(result):
            if result.success:
                try:
                    self.adb.run(f"pull {remote_path} {local_path}")
                    self.adb.run(f"shell rm {remote_path}")
                except Exception as e:
                    logger.error(f"Error saving screen recording: {str(e)}")
        
        return self.adb.run_async(cmd, callback)
    
    def backup(self, local_path: str, packages: Optional[List[str]] = None, 
              include_apks: bool = True, include_shared: bool = False, 
              include_system: bool = False) -> str:
        """
        Sao lưu dữ liệu thiết bị.
        
        Args:
            local_path: Đường dẫn lưu file sao lưu
            packages: Danh sách package cần sao lưu (None để sao lưu tất cả)
            include_apks: Bao gồm các file APK
            include_shared: Bao gồm dữ liệu chia sẻ
            include_system: Bao gồm ứng dụng hệ thống
            
        Returns:
            Kết quả lệnh
        """
        cmd = "backup"
        
        if include_apks:
            cmd += " -apk"
        else:
            cmd += " -noapk"
        
        if include_system:
            cmd += " -system"
        else:
            cmd += " -nosystem"
        
        if include_shared:
            cmd += " -shared"
        else:
            cmd += " -noshared"
        
        if packages:
            cmd += " " + " ".join(packages)
        else:
            cmd += " -all"
        
        cmd += f" -f {local_path}"
        
        logger.debug(f"Backing up device to {local_path}")
        return self.adb.run(cmd)
    
    def restore(self, local_path: str) -> str:
        """
        Khôi phục dữ liệu thiết bị.
        
        Args:
            local_path: Đường dẫn file sao lưu
            
        Returns:
            Kết quả lệnh
        """
        logger.debug(f"Restoring device from {local_path}")
        return self.adb.run(f"restore {local_path}")
    
    def start_activity(self, intent: str) -> str:
        """
        Khởi động activity.
        
        Args:
            intent: Intent để khởi động
            
        Returns:
            Kết quả lệnh
        """
        logger.debug(f"Starting activity with intent: {intent}")
        return self.adb.run(f"shell am start {intent}")
    
    def start_service(self, intent: str) -> str:
        """
        Khởi động service.
        
        Args:
            intent: Intent để khởi động
            
        Returns:
            Kết quả lệnh
        """
        logger.debug(f"Starting service with intent: {intent}")
        return self.adb.run(f"shell am startservice {intent}")
    
    def broadcast(self, intent: str) -> str:
        """
        Gửi broadcast.
        
        Args:
            intent: Intent để gửi
            
        Returns:
            Kết quả lệnh
        """
        logger.debug(f"Broadcasting intent: {intent}")
        return self.adb.run(f"shell am broadcast {intent}")
    
    def set_prop(self, prop: str, value: str) -> str:
        """
        Đặt thuộc tính hệ thống.
        
        Args:
            prop: Tên thuộc tính
            value: Giá trị
            
        Returns:
            Kết quả lệnh
        """
        logger.debug(f"Setting property {prop} to {value}")
        return self.adb.run(f"shell setprop {prop} {value}")
    
    def get_prop(self, prop: str) -> str:
        """
        Lấy thuộc tính hệ thống.
        
        Args:
            prop: Tên thuộc tính
            
        Returns:
            Giá trị thuộc tính
        """
        logger.debug(f"Getting property {prop}")
        return self.adb.run(f"shell getprop {prop}")
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """
        Lấy thông tin CPU.
        
        Returns:
            Dictionary chứa thông tin CPU
        """
        try:
            logger.debug("Getting CPU information")
            output = self.adb.run("shell cat /proc/cpuinfo")
            cpu_info = {}
            current_processor = None
            
            for line in output.splitlines():
                line = line.strip()
                if not line:
                    continue
                
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == "processor":
                        current_processor = f"processor_{value}"
                        cpu_info[current_processor] = {}
                    elif current_processor:
                        cpu_info[current_processor][key] = value
                    else:
                        cpu_info[key] = value
            
            return cpu_info
        except ADBCommandError as e:
            logger.error(f"Error getting CPU info: {e}")
            return {}
    
    def get_memory_info(self) -> Dict[str, Any]:
        """
        Lấy thông tin bộ nhớ.
        
        Returns:
            Dictionary chứa thông tin bộ nhớ
        """
        try:
            logger.debug("Getting memory information")
            output = self.adb.run("shell cat /proc/meminfo")
            mem_info = {}
            
            for line in output.splitlines():
                line = line.strip()
                if not line or ":" not in line:
                    continue
                
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                
                # Trích xuất số và đơn vị
                parts = value.split()
                if len(parts) > 0 and parts[0].isdigit():
                    mem_info[key] = {
                        "value": int(parts[0]),
                        "unit": parts[1] if len(parts) > 1 else ""
                    }
                else:
                    mem_info[key] = value
            
            return mem_info
        except ADBCommandError as e:
            logger.error(f"Error getting memory info: {e}")
            return {}
    
    def get_disk_info(self) -> Dict[str, Any]:
        """
        Lấy thông tin ổ đĩa.
        
        Returns:
            Dictionary chứa thông tin ổ đĩa
        """
        try:
            logger.debug("Getting disk information")
            output = self.adb.run("shell df")
            disk_info = {}
            
            lines = output.splitlines()
            if len(lines) < 2:
                return disk_info
            
            headers = lines[0].split()
            
            for line in lines[1:]:
                parts = line.split()
                if len(parts) < len(headers):
                    continue
                
                filesystem = parts[0]
                info = {}
                
                for i in range(1, len(headers)):
                    info[headers[i].lower()] = parts[i]
                
                disk_info[filesystem] = info
            
            return disk_info
        except ADBCommandError as e:
            logger.error(f"Error getting disk info: {e}")
            return {}
    
    def get_network_info(self) -> Dict[str, Any]:
        """
        Lấy thông tin mạng.
        
        Returns:
            Dictionary chứa thông tin mạng
        """
        try:
            logger.debug("Getting network information")
            output = self.adb.run("shell ip addr")
            network_info = {}
            
            current_interface = None
            
            for line in output.splitlines():
                line = line.strip()
                if not line:
                    continue
                
                if line[0].isdigit() and ":" in line:
                    # Dòng mới bắt đầu với interface
                    parts = line.split(":", 1)
                    interface_name = parts[1].strip()
                    current_interface = interface_name
                    network_info[current_interface] = {
                        "addresses": []
                    }
                elif current_interface and "inet " in line:
                    # Địa chỉ IPv4
                    addr = line.split("inet ")[1].split("/")[0]
                    network_info[current_interface]["addresses"].append({
                        "type": "ipv4",
                        "address": addr
                    })
                elif current_interface and "inet6 " in line:
                    # Địa chỉ IPv6
                    addr = line.split("inet6 ")[1].split("/")[0]
                    network_info[current_interface]["addresses"].append({
                        "type": "ipv6",
                        "address": addr
                    })
                elif current_interface and "link/ether " in line:
                    # Địa chỉ MAC
                    mac = line.split("link/ether ")[1].split()[0]
                    network_info[current_interface]["mac"] = mac
            
            return network_info
        except ADBCommandError as e:
            logger.error(f"Error getting network info: {e}")
            return {}
    
    def get_wifi_info(self) -> Dict[str, Any]:
        """
        Lấy thông tin WiFi.
        
        Returns:
            Dictionary chứa thông tin WiFi
        """
        try:
            logger.debug("Getting WiFi information")
            output = self.adb.run("shell dumpsys wifi")
            wifi_info = {}
            
            # Trích xuất thông tin mạng WiFi hiện tại
            if "mNetworkInfo" in output:
                network_section = output.split("mNetworkInfo")[1].split("\n")[0]
                if "state: " in network_section:
                    wifi_info["state"] = network_section.split("state: ")[1].split(",")[0]
            
            # Trích xuất thông tin SSID
            if "mWifiInfo" in output:
                wifi_section = output.split("mWifiInfo")[1].split("}\n")[0] + "}"
                for line in wifi_section.splitlines():
                    line = line.strip()
                    if "SSID: " in line:
                        wifi_info["ssid"] = line.split("SSID: ")[1].strip()
                    elif "BSSID: " in line:
                        wifi_info["bssid"] = line.split("BSSID: ")[1].strip()
                    elif "MAC: " in line:
                        wifi_info["mac"] = line.split("MAC: ")[1].strip()
                    elif "Supplicant state: " in line:
                        wifi_info["supplicant_state"] = line.split("Supplicant state: ")[1].strip()
                    elif "RSSI: " in line:
                        try:
                            wifi_info["rssi"] = int(line.split("RSSI: ")[1].split()[0])
                        except ValueError:
                            pass
                    elif "Link speed: " in line:
                        try:
                            speed_parts = line.split("Link speed: ")[1].split()
                            wifi_info["link_speed"] = {
                                "value": int(speed_parts[0]),
                                "unit": speed_parts[1] if len(speed_parts) > 1 else ""
                            }
                        except ValueError:
                            pass
            
            return wifi_info
        except ADBCommandError as e:
            logger.error(f"Error getting WiFi info: {e}")
            return {}
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Lấy thông tin tổng hợp về hệ thống.
        
        Returns:
            Dictionary chứa thông tin hệ thống
        """
        logger.debug("Getting system information")
        return {
            "device": self.get_device_info(),
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "disk": self.get_disk_info(),
            "network": self.get_network_info(),
            "wifi": self.get_wifi_info()
        }
