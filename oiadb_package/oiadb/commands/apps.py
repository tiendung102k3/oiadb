"""
Các lệnh quản lý ứng dụng trên thiết bị Android.
"""

import os
import logging
from typing import Optional, List, Dict, Any

from ..exceptions import ADBCommandError, InstallationError, UninstallationError, PackageNotFoundError

logger = logging.getLogger('my_adb_lib')

class AppCommands:
    """
    Lớp chứa các lệnh quản lý ứng dụng trên thiết bị Android.
    """
    
    def __init__(self, adb_runner):
        """
        Khởi tạo đối tượng AppCommands.
        
        Args:
            adb_runner: Đối tượng thực thi lệnh ADB
        """
        self.adb = adb_runner
    
    def install(self, apk_path: str, replace: bool = False, 
               grant_permissions: bool = False, downgrade: bool = False,
               allow_test_packages: bool = False) -> str:
        """
        Cài đặt ứng dụng từ file APK.
        
        Args:
            apk_path: Đường dẫn đến file APK
            replace: Thay thế ứng dụng nếu đã tồn tại
            grant_permissions: Tự động cấp tất cả quyền cho ứng dụng
            downgrade: Cho phép hạ cấp phiên bản ứng dụng
            allow_test_packages: Cho phép cài đặt gói test
            
        Returns:
            Kết quả lệnh
            
        Raises:
            InstallationError: Nếu cài đặt thất bại
        """
        if not os.path.exists(apk_path):
            raise InstallationError(apk_path, "File APK không tồn tại")
        
        options = []
        if replace:
            options.append("-r")
        if grant_permissions:
            options.append("-g")
        if downgrade:
            options.append("-d")
        if allow_test_packages:
            options.append("-t")
        
        try:
            logger.debug(f"Installing APK: {apk_path} with options: {options}")
            return self.adb.run(f"install {' '.join(options)} {apk_path}")
        except ADBCommandError as e:
            raise InstallationError(apk_path, e.error_message)
    
    def install_multiple(self, apk_paths: List[str], replace: bool = False, 
                        grant_permissions: bool = False) -> str:
        """
        Cài đặt nhiều APK (split APKs).
        
        Args:
            apk_paths: Danh sách đường dẫn đến các file APK
            replace: Thay thế ứng dụng nếu đã tồn tại
            grant_permissions: Tự động cấp tất cả quyền cho ứng dụng
            
        Returns:
            Kết quả lệnh
            
        Raises:
            InstallationError: Nếu cài đặt thất bại
        """
        for apk_path in apk_paths:
            if not os.path.exists(apk_path):
                raise InstallationError(apk_path, "File APK không tồn tại")
        
        options = ["-m"]
        if replace:
            options.append("-r")
        if grant_permissions:
            options.append("-g")
        
        try:
            logger.debug(f"Installing multiple APKs: {apk_paths}")
            return self.adb.run(f"install-multiple {' '.join(options)} {' '.join(apk_paths)}")
        except ADBCommandError as e:
            raise InstallationError(str(apk_paths), e.error_message)
    
    def uninstall(self, package_name: str, keep_data: bool = False) -> str:
        """
        Gỡ cài đặt ứng dụng.
        
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
            logger.debug(f"Uninstalling package: {package_name}")
            return self.adb.run(f"uninstall {' '.join(options)} {package_name}")
        except ADBCommandError as e:
            raise UninstallationError(package_name, e.error_message)
    
    def list_packages(self, filter_type: Optional[str] = None) -> List[str]:
        """
        Liệt kê các package đã cài đặt.
        
        Args:
            filter_type: Loại filter (None, 'system', 'third-party', 'disabled', 'enabled')
            
        Returns:
            Danh sách tên package
        """
        cmd = "shell pm list packages"
        
        if filter_type:
            if filter_type == "system":
                cmd += " -s"
            elif filter_type == "third-party":
                cmd += " -3"
            elif filter_type == "disabled":
                cmd += " -d"
            elif filter_type == "enabled":
                cmd += " -e"
        
        try:
            logger.debug(f"Listing packages with filter: {filter_type}")
            output = self.adb.run(cmd)
            packages = []
            
            for line in output.splitlines():
                if line.startswith("package:"):
                    packages.append(line[8:])
            
            return packages
        except ADBCommandError as e:
            logger.error(f"Error listing packages: {e}")
            return []
    
    def clear_app_data(self, package_name: str) -> str:
        """
        Xóa dữ liệu ứng dụng.
        
        Args:
            package_name: Tên package của ứng dụng
            
        Returns:
            Kết quả lệnh
        """
        logger.debug(f"Clearing app data for package: {package_name}")
        return self.adb.run(f"shell pm clear {package_name}")
    
    def force_stop(self, package_name: str) -> str:
        """
        Dừng ứng dụng.
        
        Args:
            package_name: Tên package của ứng dụng
            
        Returns:
            Kết quả lệnh
        """
        logger.debug(f"Force stopping package: {package_name}")
        return self.adb.run(f"shell am force-stop {package_name}")
    
    def start_app(self, package_name: str, activity: Optional[str] = None) -> str:
        """
        Khởi động ứng dụng.
        
        Args:
            package_name: Tên package của ứng dụng
            activity: Tên activity để khởi động (tùy chọn)
            
        Returns:
            Kết quả lệnh
        """
        if activity:
            logger.debug(f"Starting activity: {package_name}/{activity}")
            return self.adb.run(f"shell am start -n {package_name}/{activity}")
        else:
            logger.debug(f"Starting package: {package_name}")
            return self.adb.run(f"shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
    
    def get_app_version(self, package_name: str) -> str:
        """
        Lấy phiên bản của ứng dụng.
        
        Args:
            package_name: Tên package của ứng dụng
            
        Returns:
            Phiên bản ứng dụng
            
        Raises:
            PackageNotFoundError: Nếu package không tồn tại
        """
        try:
            logger.debug(f"Getting version for package: {package_name}")
            output = self.adb.run(f"shell dumpsys package {package_name}")
            for line in output.splitlines():
                if "versionName" in line:
                    return line.split("=", 1)[1].strip()
            
            raise PackageNotFoundError(package_name)
        except ADBCommandError:
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
            logger.debug(f"Checking if package is installed: {package_name}")
            output = self.adb.run(f"shell pm list packages {package_name}")
            return package_name in output
        except ADBCommandError:
            return False
    
    def get_app_path(self, package_name: str) -> str:
        """
        Lấy đường dẫn của ứng dụng trên thiết bị.
        
        Args:
            package_name: Tên package của ứng dụng
            
        Returns:
            Đường dẫn của ứng dụng
            
        Raises:
            PackageNotFoundError: Nếu package không tồn tại
        """
        try:
            logger.debug(f"Getting path for package: {package_name}")
            output = self.adb.run(f"shell pm path {package_name}")
            if output.startswith("package:"):
                return output[8:].strip()
            raise PackageNotFoundError(package_name)
        except ADBCommandError:
            raise PackageNotFoundError(package_name)
    
    def get_app_info(self, package_name: str) -> Dict[str, Any]:
        """
        Lấy thông tin chi tiết về ứng dụng.
        
        Args:
            package_name: Tên package của ứng dụng
            
        Returns:
            Dictionary chứa thông tin ứng dụng
            
        Raises:
            PackageNotFoundError: Nếu package không tồn tại
        """
        try:
            logger.debug(f"Getting info for package: {package_name}")
            output = self.adb.run(f"shell dumpsys package {package_name}")
            
            if "Unable to find package" in output:
                raise PackageNotFoundError(package_name)
            
            info = {
                "package_name": package_name,
                "version_name": None,
                "version_code": None,
                "first_install_time": None,
                "last_update_time": None,
                "installer": None,
                "uid": None,
                "target_sdk": None,
                "permissions": []
            }
            
            for line in output.splitlines():
                line = line.strip()
                
                if "versionName=" in line:
                    info["version_name"] = line.split("=", 1)[1].strip()
                elif "versionCode=" in line:
                    version_code_str = line.split("=", 1)[1].strip().split(" ")[0]
                    try:
                        info["version_code"] = int(version_code_str)
                    except ValueError:
                        info["version_code"] = version_code_str
                elif "firstInstallTime=" in line:
                    info["first_install_time"] = line.split("=", 1)[1].strip()
                elif "lastUpdateTime=" in line:
                    info["last_update_time"] = line.split("=", 1)[1].strip()
                elif "installerPackageName=" in line:
                    installer = line.split("=", 1)[1].strip()
                    if installer:
                        info["installer"] = installer
                elif "userId=" in line:
                    try:
                        info["uid"] = int(line.split("=", 1)[1].strip())
                    except ValueError:
                        pass
                elif "targetSdk=" in line:
                    try:
                        info["target_sdk"] = int(line.split("=", 1)[1].strip())
                    except ValueError:
                        pass
                elif "granted=true" in line and "permission." in line:
                    # Extract permission name
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        permission = parts[0].strip()
                        info["permissions"].append(permission)
            
            return info
        
        except ADBCommandError:
            raise PackageNotFoundError(package_name)
    
    def get_running_apps(self) -> List[str]:
        """
        Lấy danh sách các ứng dụng đang chạy.
        
        Returns:
            Danh sách tên package của các ứng dụng đang chạy
        """
        try:
            logger.debug("Getting running apps")
            output = self.adb.run("shell ps")
            packages = set()
            
            for line in output.splitlines():
                if "com." in line:
                    parts = line.split()
                    if len(parts) >= 9:
                        package = parts[8]
                        if ":" in package:
                            package = package.split(":", 1)[0]
                        if package.startswith("com."):
                            packages.add(package)
            
            return list(packages)
        except ADBCommandError as e:
            logger.error(f"Error getting running apps: {e}")
            return []
    
    def get_app_activities(self, package_name: str) -> List[str]:
        """
        Lấy danh sách các activity của ứng dụng.
        
        Args:
            package_name: Tên package của ứng dụng
            
        Returns:
            Danh sách tên các activity
            
        Raises:
            PackageNotFoundError: Nếu package không tồn tại
        """
        try:
            logger.debug(f"Getting activities for package: {package_name}")
            output = self.adb.run(f"shell dumpsys package {package_name}")
            
            if "Unable to find package" in output:
                raise PackageNotFoundError(package_name)
            
            activities = []
            in_activity_section = False
            
            for line in output.splitlines():
                if "Activity Resolver Table:" in line:
                    in_activity_section = True
                    continue
                elif "Provider Resolver Table:" in line:
                    in_activity_section = False
                    continue
                
                if in_activity_section and package_name in line and "/" in line:
                    parts = line.strip().split()
                    for part in parts:
                        if package_name in part and "/" in part:
                            activity = part.strip()
                            if activity.endswith("}"):
                                activity = activity[:-1]
                            if activity.endswith(";"):
                                activity = activity[:-1]
                            activities.append(activity)
            
            return activities
        
        except ADBCommandError:
            raise PackageNotFoundError(package_name)
    
    def grant_permission(self, package_name: str, permission: str) -> str:
        """
        Cấp quyền cho ứng dụng.
        
        Args:
            package_name: Tên package của ứng dụng
            permission: Quyền cần cấp
            
        Returns:
            Kết quả lệnh
        """
        logger.debug(f"Granting permission {permission} to package: {package_name}")
        return self.adb.run(f"shell pm grant {package_name} {permission}")
    
    def revoke_permission(self, package_name: str, permission: str) -> str:
        """
        Thu hồi quyền của ứng dụng.
        
        Args:
            package_name: Tên package của ứng dụng
            permission: Quyền cần thu hồi
            
        Returns:
            Kết quả lệnh
        """
        logger.debug(f"Revoking permission {permission} from package: {package_name}")
        return self.adb.run(f"shell pm revoke {package_name} {permission}")
    
    def disable_app(self, package_name: str) -> str:
        """
        Vô hiệu hóa ứng dụng.
        
        Args:
            package_name: Tên package của ứng dụng
            
        Returns:
            Kết quả lệnh
        """
        logger.debug(f"Disabling package: {package_name}")
        return self.adb.run(f"shell pm disable-user {package_name}")
    
    def enable_app(self, package_name: str) -> str:
        """
        Kích hoạt ứng dụng.
        
        Args:
            package_name: Tên package của ứng dụng
            
        Returns:
            Kết quả lệnh
        """
        logger.debug(f"Enabling package: {package_name}")
        return self.adb.run(f"shell pm enable {package_name}")
