"""
Tiện ích tự động cài đặt và quản lý ADB.
"""

import os
import sys
import platform
import subprocess
import logging
import tempfile
import shutil
import zipfile
import tarfile
import requests
from typing import Optional, List, Dict, Any, Union

from ..utils.platform_utils import get_platform_info, PlatformInfo

logger = logging.getLogger('oiadb')

class ADBManager:
    """Lớp quản lý cài đặt và cấu hình ADB."""
    
    def __init__(self, install_dir: Optional[str] = None):
        """
        Khởi tạo ADBManager.
        
        Args:
            install_dir: Thư mục cài đặt ADB, mặc định là thư mục người dùng
        """
        self.platform_info = get_platform_info()
        
        # Xác định thư mục cài đặt
        if install_dir:
            self.install_dir = install_dir
        else:
            # Thư mục mặc định dựa trên nền tảng
            if self.platform_info.is_windows:
                self.install_dir = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'oiadb', 'platform-tools')
            elif self.platform_info.is_termux:
                self.install_dir = os.path.join(os.environ.get('HOME', ''), '.oiadb', 'platform-tools')
            else:
                self.install_dir = os.path.join(os.environ.get('HOME', ''), '.oiadb', 'platform-tools')
        
        # Đảm bảo thư mục cài đặt tồn tại
        os.makedirs(self.install_dir, exist_ok=True)
        
        # Xác định đường dẫn ADB
        self.adb_name = "adb.exe" if self.platform_info.is_windows else "adb"
        self.adb_path = os.path.join(self.install_dir, self.adb_name)
    
    def get_download_url(self) -> Optional[str]:
        """
        Lấy URL tải xuống ADB phù hợp với nền tảng.
        
        Returns:
            URL tải xuống hoặc None nếu không hỗ trợ nền tảng
        """
        # URL cơ sở cho các phiên bản mới nhất
        base_url = "https://dl.google.com/android/repository/platform-tools-latest-"
        
        if self.platform_info.is_windows:
            return base_url + "windows.zip"
        elif self.platform_info.is_macos:
            return base_url + "darwin.zip"
        elif self.platform_info.is_linux and not self.platform_info.is_android:
            return base_url + "linux.zip"
        elif self.platform_info.is_termux:
            # Termux sử dụng package manager riêng
            return None
        
        return None
    
    def download_adb(self) -> Optional[str]:
        """
        Tải xuống gói ADB.
        
        Returns:
            Đường dẫn đến file đã tải xuống hoặc None nếu thất bại
        """
        download_url = self.get_download_url()
        if not download_url:
            logger.error("Không hỗ trợ tải xuống ADB tự động cho nền tảng này")
            return None
        
        # Tạo thư mục tạm thời
        temp_dir = tempfile.mkdtemp()
        archive_path = os.path.join(temp_dir, "platform-tools.zip")
        
        try:
            logger.info(f"Đang tải xuống ADB từ {download_url}...")
            response = requests.get(download_url, stream=True, timeout=60)
            response.raise_for_status()
            
            with open(archive_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Đã tải xuống ADB thành công: {archive_path}")
            return archive_path
        except Exception as e:
            logger.error(f"Lỗi khi tải xuống ADB: {e}")
            return None
    
    def extract_adb(self, archive_path: str) -> bool:
        """
        Giải nén gói ADB.
        
        Args:
            archive_path: Đường dẫn đến file nén
            
        Returns:
            True nếu giải nén thành công, False nếu không
        """
        try:
            logger.info(f"Đang giải nén {archive_path} vào {self.install_dir}...")
            
            # Xóa thư mục cài đặt cũ nếu tồn tại
            if os.path.exists(self.install_dir):
                shutil.rmtree(self.install_dir)
            
            # Tạo thư mục cài đặt mới
            os.makedirs(self.install_dir, exist_ok=True)
            
            # Giải nén
            if archive_path.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(os.path.dirname(self.install_dir))
            elif archive_path.endswith(('.tar.gz', '.tgz')):
                with tarfile.open(archive_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(os.path.dirname(self.install_dir))
            else:
                logger.error(f"Không hỗ trợ định dạng file: {archive_path}")
                return False
            
            # Đảm bảo quyền thực thi
            if not self.platform_info.is_windows:
                os.chmod(self.adb_path, 0o755)
            
            logger.info(f"Đã giải nén ADB thành công vào {self.install_dir}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi giải nén ADB: {e}")
            return False
    
    def install_adb_termux(self) -> bool:
        """
        Cài đặt ADB trên Termux.
        
        Returns:
            True nếu cài đặt thành công, False nếu không
        """
        try:
            logger.info("Đang cài đặt ADB trên Termux...")
            
            # Sử dụng package manager của Termux
            process = subprocess.run(
                ["pkg", "install", "-y", "android-tools"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                # text=True,  # Không sử dụng cho Python 3.6
            )
            
            stdout_str = process.stdout.decode(errors='ignore')
            stderr_str = process.stderr.decode(errors='ignore')
            
            if process.returncode != 0:
                logger.error(f"Lỗi khi cài đặt ADB trên Termux: {stderr_str}")
                return False
            
            logger.info("Đã cài đặt ADB thành công trên Termux")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi cài đặt ADB trên Termux: {e}")
            return False
    
    def install_adb(self) -> Optional[str]:
        """
        Cài đặt ADB.
        
        Returns:
            Đường dẫn đến ADB đã cài đặt hoặc None nếu thất bại
        """
        # Kiểm tra xem ADB đã được cài đặt chưa
        if os.path.exists(self.adb_path) and os.access(self.adb_path, os.X_OK):
            logger.info(f"ADB đã được cài đặt tại: {self.adb_path}")
            return self.adb_path
        
        # Xử lý đặc biệt cho Termux
        if self.platform_info.is_termux:
            if self.install_adb_termux():
                adb_path = shutil.which("adb")
                if adb_path:
                    logger.info(f"ADB đã được cài đặt trên Termux tại: {adb_path}")
                    return adb_path
                else:
                    logger.error("Không tìm thấy ADB sau khi cài đặt trên Termux")
                    return None
            else:
                logger.error("Không thể cài đặt ADB trên Termux")
                return None
        
        # Tải xuống và cài đặt cho các nền tảng khác
        archive_path = self.download_adb()
        if not archive_path:
            return None
        
        if self.extract_adb(archive_path):
            # Xóa file tạm
            try:
                os.remove(archive_path)
                shutil.rmtree(os.path.dirname(archive_path))
            except:
                pass
            
            logger.info(f"ADB đã được cài đặt tại: {self.adb_path}")
            return self.adb_path
        
        return None
    
    def find_adb(self) -> Optional[str]:
        """
        Tìm đường dẫn đến ADB trong hệ thống.
        
        Returns:
            Đường dẫn đến ADB nếu tìm thấy, None nếu không
        """
        # Kiểm tra trong thư mục cài đặt
        if os.path.exists(self.adb_path) and os.access(self.adb_path, os.X_OK):
            logger.debug(f"Tìm thấy ADB trong thư mục cài đặt: {self.adb_path}")
            return self.adb_path
        
        # Kiểm tra trong PATH
        adb_in_path = shutil.which(self.adb_name)
        if adb_in_path:
            logger.debug(f"Tìm thấy ADB trong PATH: {adb_in_path}")
            return adb_in_path
        
        # Kiểm tra các đường dẫn mặc định
        for path in self.platform_info.adb_default_paths:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                logger.debug(f"Tìm thấy ADB tại vị trí mặc định: {path}")
                return path
        
        logger.debug("Không tìm thấy ADB trong hệ thống")
        return None
    
    def get_adb_version(self, adb_path: str) -> Optional[str]:
        """
        Lấy phiên bản của ADB.
        
        Args:
            adb_path: Đường dẫn đến ADB
            
        Returns:
            Chuỗi phiên bản hoặc None nếu không thể lấy
        """
        try:
            process = subprocess.run(
                [adb_path, "version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                # text=True,  # Không sử dụng cho Python 3.6
            )
            
            stdout_str = process.stdout.decode(errors='ignore')
            
            if process.returncode == 0 and stdout_str:
                # Phân tích chuỗi phiên bản
                # Ví dụ: "Android Debug Bridge version 1.0.41"
                lines = stdout_str.splitlines()
                if lines and "version" in lines[0]:
                    version_parts = lines[0].split("version")
                    if len(version_parts) >= 2:
                        return version_parts[1].strip()
            
            return None
        except Exception as e:
            logger.error(f"Lỗi khi lấy phiên bản ADB: {e}")
            return None
    
    def ensure_adb_available(self) -> Optional[str]:
        """
        Đảm bảo ADB có sẵn, cài đặt nếu cần.
        
        Returns:
            Đường dẫn đến ADB nếu có sẵn hoặc cài đặt thành công, None nếu không
        """
        # Tìm ADB trong hệ thống
        adb_path = self.find_adb()
        if adb_path:
            logger.info(f"Đã tìm thấy ADB tại: {adb_path}")
            return adb_path
        
        # Cài đặt ADB nếu không tìm thấy
        logger.info("Không tìm thấy ADB, đang cài đặt...")
        return self.install_adb()
