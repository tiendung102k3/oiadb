"""
Tiện ích xử lý tương thích đa nền tảng cho thư viện OIADB.
"""

import os
import sys
import platform
import subprocess
import logging
import tempfile
import shutil
from typing import Optional, Tuple, List, Dict, Any, Union

logger = logging.getLogger('oiadb')

class PlatformInfo:
    """Lớp cung cấp thông tin về nền tảng hiện tại và các tiện ích tương thích."""
    
    def __init__(self):
        """Khởi tạo và phát hiện thông tin nền tảng."""
        self.os_name = platform.system().lower()  # 'windows', 'linux', 'darwin'
        self.is_windows = self.os_name == 'windows'
        self.is_linux = self.os_name == 'linux'
        self.is_macos = self.os_name == 'darwin'
        self.is_termux = self._detect_termux()
        self.is_android = self._detect_android()
        self.path_separator = os.path.sep
        self.line_separator = os.linesep
        self.temp_dir = tempfile.gettempdir()
        self.home_dir = os.path.expanduser("~")
        self.adb_default_paths = self._get_default_adb_paths()
        
        logger.debug(f"Detected platform: {self.os_name}")
        logger.debug(f"Is Termux: {self.is_termux}")
        logger.debug(f"Is Android: {self.is_android}")
        logger.debug(f"Temp directory: {self.temp_dir}")
        logger.debug(f"Home directory: {self.home_dir}")
    
    def _detect_termux(self) -> bool:
        """Phát hiện xem đang chạy trong Termux hay không."""
        # Kiểm tra biến môi trường đặc trưng của Termux
        if 'TERMUX_VERSION' in os.environ:
            return True
        
        # Kiểm tra đường dẫn Termux
        termux_paths = ['/data/data/com.termux', '/data/data/com.termux/files/usr']
        for path in termux_paths:
            if os.path.exists(path):
                return True
        
        return False
    
    def _detect_android(self) -> bool:
        """Phát hiện xem đang chạy trên Android (không phải Termux) hay không."""
        if self.is_termux:
            return True  # Termux chạy trên Android
        
        # Kiểm tra các đường dẫn đặc trưng của Android
        android_paths = ['/system/app/', '/data/app/']
        for path in android_paths:
            if os.path.exists(path):
                return True
        
        return False
    
    def _get_default_adb_paths(self) -> List[str]:
        """Lấy danh sách các đường dẫn mặc định có thể chứa ADB."""
        paths = []
        
        if self.is_windows:
            # Đường dẫn Windows phổ biến
            paths.extend([
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Android', 'Sdk', 'platform-tools', 'adb.exe'),
                os.path.join(os.environ.get('PROGRAMFILES', ''), 'Android', 'android-sdk', 'platform-tools', 'adb.exe'),
                os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Android', 'android-sdk', 'platform-tools', 'adb.exe'),
            ])
        elif self.is_macos:
            # Đường dẫn macOS phổ biến
            paths.extend([
                os.path.join(self.home_dir, 'Library', 'Android', 'sdk', 'platform-tools', 'adb'),
                '/usr/local/bin/adb',
            ])
        elif self.is_linux:
            # Đường dẫn Linux phổ biến
            paths.extend([
                os.path.join(self.home_dir, 'Android', 'Sdk', 'platform-tools', 'adb'),
                '/usr/local/bin/adb',
                '/usr/bin/adb',
            ])
            
            # Đường dẫn Termux
            if self.is_termux:
                paths.extend([
                    os.path.join(os.environ.get('PREFIX', ''), 'bin', 'adb'),
                ])
        
        return paths
    
    def find_adb_path(self) -> Optional[str]:
        """
        Tìm đường dẫn đến ADB trong hệ thống.
        
        Returns:
            Đường dẫn đến ADB nếu tìm thấy, None nếu không
        """
        # Kiểm tra trong PATH
        adb_name = 'adb.exe' if self.is_windows else 'adb'
        adb_in_path = shutil.which(adb_name)
        if adb_in_path:
            logger.debug(f"Found ADB in PATH: {adb_in_path}")
            return adb_in_path
        
        # Kiểm tra các đường dẫn mặc định
        for path in self.adb_default_paths:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                logger.debug(f"Found ADB at default location: {path}")
                return path
        
        logger.debug("ADB not found in system")
        return None
    
    def get_device_temp_dir(self) -> str:
        """
        Lấy đường dẫn thư mục tạm thời trên thiết bị Android.
        
        Returns:
            Đường dẫn thư mục tạm thời phù hợp với thiết bị
        """
        # Đường dẫn mặc định cho hầu hết các thiết bị
        default_temp = "/sdcard"
        
        # Có thể mở rộng để phát hiện các đường dẫn khác nhau dựa trên thiết bị
        # Ví dụ: một số thiết bị có thể sử dụng /storage/emulated/0 thay vì /sdcard
        
        return default_temp
    
    def normalize_path(self, path: str) -> str:
        """
        Chuẩn hóa đường dẫn cho nền tảng hiện tại.
        
        Args:
            path: Đường dẫn cần chuẩn hóa
            
        Returns:
            Đường dẫn đã chuẩn hóa
        """
        # Chuyển đổi dấu gạch chéo sang dấu gạch chéo ngược trên Windows
        if self.is_windows:
            path = path.replace('/', '\\')
        else:
            path = path.replace('\\', '/')
        
        # Xử lý đường dẫn tương đối
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        
        return path
    
    def create_process_args(self, command: List[str], **kwargs) -> Dict[str, Any]:
        """
        Tạo đối số cho subprocess.Popen phù hợp với nền tảng.
        
        Args:
            command: Danh sách các thành phần lệnh
            **kwargs: Các đối số bổ sung cho Popen
            
        Returns:
            Dict chứa các đối số cho Popen
        """
        args = {
            'args': command,
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
            # 'text': True,  # Không sử dụng cho Python 3.6
            'bufsize': 1,
        }
        
        # Thêm các đối số đặc thù cho Windows
        if self.is_windows:
            args['creationflags'] = subprocess.CREATE_NO_WINDOW
        
        # Ghi đè bằng các đối số được cung cấp
        args.update(kwargs)
        
        return args
    
    def kill_process(self, process: subprocess.Popen) -> bool:
        """
        Kết thúc tiến trình một cách an toàn trên đa nền tảng.
        
        Args:
            process: Đối tượng tiến trình cần kết thúc
            
        Returns:
            True nếu kết thúc thành công, False nếu không
        """
        try:
            if self.is_windows:
                import ctypes
                PROCESS_TERMINATE = 1
                handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, process.pid)
                ctypes.windll.kernel32.TerminateProcess(handle, -1)
                ctypes.windll.kernel32.CloseHandle(handle)
            else:
                import signal
                os.kill(process.pid, signal.SIGTERM)
                process.wait(timeout=3)  # Đợi tiến trình kết thúc
            return True
        except Exception as e:
            logger.error(f"Error killing process: {e}")
            try:
                process.kill()  # Thử phương pháp mạnh hơn
                return True
            except Exception as e2:
                logger.error(f"Failed to forcefully kill process: {e2}")
                return False
    
    def download_file(self, url: str, output_path: str) -> bool:
        """
        Tải xuống file từ URL.
        
        Args:
            url: URL của file cần tải xuống
            output_path: Đường dẫn lưu file
            
        Returns:
            True nếu tải xuống thành công, False nếu không
        """
        try:
            import requests
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.debug(f"Downloaded file from {url} to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error downloading file from {url}: {e}")
            return False
    
    def extract_archive(self, archive_path: str, extract_dir: str) -> bool:
        """
        Giải nén file nén.
        
        Args:
            archive_path: Đường dẫn đến file nén
            extract_dir: Thư mục giải nén
            
        Returns:
            True nếu giải nén thành công, False nếu không
        """
        try:
            import zipfile
            import tarfile
            
            os.makedirs(extract_dir, exist_ok=True)
            
            if archive_path.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            elif archive_path.endswith(('.tar.gz', '.tgz')):
                with tarfile.open(archive_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(extract_dir)
            elif archive_path.endswith('.tar'):
                with tarfile.open(archive_path, 'r') as tar_ref:
                    tar_ref.extractall(extract_dir)
            else:
                logger.error(f"Unsupported archive format: {archive_path}")
                return False
            
            logger.debug(f"Extracted {archive_path} to {extract_dir}")
            return True
        except Exception as e:
            logger.error(f"Error extracting archive {archive_path}: {e}")
            return False

# Tạo một instance toàn cục để sử dụng trong toàn bộ thư viện
platform_info = PlatformInfo()

def get_platform_info() -> PlatformInfo:
    """
    Lấy thông tin nền tảng.
    
    Returns:
        Đối tượng PlatformInfo
    """
    return platform_info

class ADBInstaller:
    """Lớp hỗ trợ tải xuống và cài đặt ADB."""
    
    def __init__(self, install_dir: Optional[str] = None):
        """
        Khởi tạo ADBInstaller.
        
        Args:
            install_dir: Thư mục cài đặt ADB, mặc định là thư mục tạm thời
        """
        self.platform = get_platform_info()
        self.install_dir = install_dir or os.path.join(self.platform.temp_dir, 'oiadb_adb')
        os.makedirs(self.install_dir, exist_ok=True)
    
    def get_download_url(self) -> Optional[str]:
        """
        Lấy URL tải xuống ADB phù hợp với nền tảng.
        
        Returns:
            URL tải xuống hoặc None nếu không hỗ trợ nền tảng
        """
        # URL cơ sở cho các phiên bản mới nhất
        base_url = "https://dl.google.com/android/repository/platform-tools-latest-"
        
        if self.platform.is_windows:
            return base_url + "windows.zip"
        elif self.platform.is_macos:
            return base_url + "darwin.zip"
        elif self.platform.is_linux and not self.platform.is_android:
            return base_url + "linux.zip"
        elif self.platform.is_termux:
            # Termux sử dụng package manager riêng
            return None
        
        return None
    
    def install_adb(self) -> Optional[str]:
        """
        Tải xuống và cài đặt ADB.
        
        Returns:
            Đường dẫn đến ADB đã cài đặt hoặc None nếu thất bại
        """
        # Kiểm tra xem ADB đã được cài đặt chưa
        existing_adb = self.platform.find_adb_path()
        if existing_adb:
            logger.info(f"ADB already installed at: {existing_adb}")
            return existing_adb
        
        # Xử lý đặc biệt cho Termux
        if self.platform.is_termux:
            return self._install_adb_termux()
        
        # Tải xuống và cài đặt cho các nền tảng khác
        download_url = self.get_download_url()
        if not download_url:
            logger.error("Unsupported platform for automatic ADB installation")
            return None
        
        # Tải xuống file nén
        archive_path = os.path.join(self.install_dir, "platform-tools.zip")
        if not self.platform.download_file(download_url, archive_path):
            return None
        
        # Giải nén
        extract_dir = os.path.join(self.install_dir, "platform-tools")
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        
        if not self.platform.extract_archive(archive_path, self.install_dir):
            return None
        
        # Tìm đường dẫn ADB
        adb_name = "adb.exe" if self.platform.is_windows else "adb"
        adb_path = os.path.join(extract_dir, adb_name)
        
        # Đảm bảo quyền thực thi
        if not self.platform.is_windows:
            os.chmod(adb_path, 0o755)
        
        logger.info(f"ADB installed at: {adb_path}")
        return adb_path
    
    def _install_adb_termux(self) -> Optional[str]:
        """
        Cài đặt ADB trên Termux.
        
        Returns:
            Đường dẫn đến ADB đã cài đặt hoặc None nếu thất bại
        """
        try:
            logger.info("Installing ADB on Termux...")
            
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
                logger.error(f"Failed to install ADB on Termux: {stderr_str}")
                return None
            
            # Kiểm tra lại sau khi cài đặt
            adb_path = shutil.which("adb")
            if adb_path:
                logger.info(f"ADB installed on Termux at: {adb_path}")
                return adb_path
            
            logger.error("ADB installation on Termux completed but ADB not found in PATH")
            return None
        except Exception as e:
            logger.error(f"Error installing ADB on Termux: {e}")
            return None
