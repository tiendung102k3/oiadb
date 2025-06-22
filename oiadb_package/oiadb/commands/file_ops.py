"""
Các lệnh thao tác file trên thiết bị Android.
"""

import os
import logging
from typing import Optional, List, Dict, Any, Union

from ..exceptions import ADBCommandError, FileOperationError
from ..utils.platform_utils import get_platform_info

logger = logging.getLogger('oiadb')

class FileOperationsCommands:
    """
    Lớp chứa các lệnh thao tác file trên thiết bị Android.
    """
    
    def __init__(self, adb_runner):
        """
        Khởi tạo đối tượng FileOperationsCommands.
        
        Args:
            adb_runner: Đối tượng thực thi lệnh ADB
        """
        self.adb = adb_runner
        self.platform_info = get_platform_info()
    
    def push(self, local_path: str, remote_path: str) -> str:
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
            return self.adb.run(f"push \"{local_path}\" \"{remote_path}\"")
        except ADBCommandError as e:
            raise FileOperationError("push", local_path, remote_path, e.error_message)
    
    def pull(self, remote_path: str, local_path: str) -> str:
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
            return self.adb.run(f"pull \"{remote_path}\" \"{local_path}\"")
        except ADBCommandError as e:
            raise FileOperationError("pull", remote_path, local_path, e.error_message)
    
    def list_files(self, remote_path: str) -> List[str]:
        """
        Liệt kê các file trong thư mục trên thiết bị.
        
        Args:
            remote_path: Đường dẫn thư mục trên thiết bị
            
        Returns:
            Danh sách các file
            
        Raises:
            FileOperationError: Nếu thao tác thất bại
        """
        try:
            output = self.adb.run(f"shell ls -la \"{remote_path}\"")
            files = []
            
            for line in output.splitlines():
                if not line.strip():
                    continue
                
                # Bỏ qua dòng tổng số
                if line.startswith("total "):
                    continue
                
                # Lấy tên file từ dòng kết quả ls
                parts = line.split()
                if len(parts) >= 8:
                    file_name = " ".join(parts[8:])
                    files.append(file_name)
            
            return files
        except ADBCommandError as e:
            raise FileOperationError("list", remote_path, "", e.error_message)
    
    def exists(self, remote_path: str) -> bool:
        """
        Kiểm tra xem file hoặc thư mục có tồn tại trên thiết bị không.
        
        Args:
            remote_path: Đường dẫn file hoặc thư mục trên thiết bị
            
        Returns:
            True nếu tồn tại, False nếu không
        """
        try:
            output = self.adb.run(f"shell [ -e \"{remote_path}\" ] && echo \"exists\" || echo \"not exists\"")
            return "exists" in output
        except ADBCommandError:
            return False
    
    def is_file(self, remote_path: str) -> bool:
        """
        Kiểm tra xem đường dẫn có phải là file không.
        
        Args:
            remote_path: Đường dẫn trên thiết bị
            
        Returns:
            True nếu là file, False nếu không
        """
        try:
            output = self.adb.run(f"shell [ -f \"{remote_path}\" ] && echo \"is file\" || echo \"not file\"")
            return "is file" in output
        except ADBCommandError:
            return False
    
    def is_dir(self, remote_path: str) -> bool:
        """
        Kiểm tra xem đường dẫn có phải là thư mục không.
        
        Args:
            remote_path: Đường dẫn trên thiết bị
            
        Returns:
            True nếu là thư mục, False nếu không
        """
        try:
            output = self.adb.run(f"shell [ -d \"{remote_path}\" ] && echo \"is dir\" || echo \"not dir\"")
            return "is dir" in output
        except ADBCommandError:
            return False
    
    def mkdir(self, remote_path: str, parents: bool = False) -> str:
        """
        Tạo thư mục trên thiết bị.
        
        Args:
            remote_path: Đường dẫn thư mục cần tạo
            parents: Tạo cả thư mục cha nếu cần
            
        Returns:
            Kết quả lệnh
            
        Raises:
            FileOperationError: Nếu thao tác thất bại
        """
        try:
            if parents:
                return self.adb.run(f"shell mkdir -p \"{remote_path}\"")
            else:
                return self.adb.run(f"shell mkdir \"{remote_path}\"")
        except ADBCommandError as e:
            raise FileOperationError("mkdir", remote_path, "", e.error_message)
    
    def remove(self, remote_path: str, recursive: bool = False, force: bool = False) -> str:
        """
        Xóa file hoặc thư mục trên thiết bị.
        
        Args:
            remote_path: Đường dẫn file hoặc thư mục cần xóa
            recursive: Xóa đệ quy (cho thư mục)
            force: Xóa mà không hỏi
            
        Returns:
            Kết quả lệnh
            
        Raises:
            FileOperationError: Nếu thao tác thất bại
        """
        try:
            options = []
            if recursive:
                options.append("-r")
            if force:
                options.append("-f")
            
            return self.adb.run(f"shell rm {' '.join(options)} \"{remote_path}\"")
        except ADBCommandError as e:
            raise FileOperationError("remove", remote_path, "", e.error_message)
    
    def copy(self, source_path: str, dest_path: str) -> str:
        """
        Sao chép file hoặc thư mục trên thiết bị.
        
        Args:
            source_path: Đường dẫn nguồn
            dest_path: Đường dẫn đích
            
        Returns:
            Kết quả lệnh
            
        Raises:
            FileOperationError: Nếu thao tác thất bại
        """
        try:
            return self.adb.run(f"shell cp -r \"{source_path}\" \"{dest_path}\"")
        except ADBCommandError as e:
            raise FileOperationError("copy", source_path, dest_path, e.error_message)
    
    def move(self, source_path: str, dest_path: str) -> str:
        """
        Di chuyển file hoặc thư mục trên thiết bị.
        
        Args:
            source_path: Đường dẫn nguồn
            dest_path: Đường dẫn đích
            
        Returns:
            Kết quả lệnh
            
        Raises:
            FileOperationError: Nếu thao tác thất bại
        """
        try:
            return self.adb.run(f"shell mv \"{source_path}\" \"{dest_path}\"")
        except ADBCommandError as e:
            raise FileOperationError("move", source_path, dest_path, e.error_message)
    
    def cat(self, remote_path: str) -> str:
        """
        Đọc nội dung file trên thiết bị.
        
        Args:
            remote_path: Đường dẫn file trên thiết bị
            
        Returns:
            Nội dung file
            
        Raises:
            FileOperationError: Nếu thao tác thất bại
        """
        try:
            return self.adb.run(f"shell cat \"{remote_path}\"")
        except ADBCommandError as e:
            raise FileOperationError("cat", remote_path, "", e.error_message)
    
    def write(self, remote_path: str, content: str) -> str:
        """
        Ghi nội dung vào file trên thiết bị.
        
        Args:
            remote_path: Đường dẫn file trên thiết bị
            content: Nội dung cần ghi
            
        Returns:
            Kết quả lệnh
            
        Raises:
            FileOperationError: Nếu thao tác thất bại
        """
        try:
            # Sử dụng đường dẫn tạm thời phù hợp với thiết bị
            device_temp_dir = self.platform_info.get_device_temp_dir()
            temp_file = f"{device_temp_dir}/oiadb_temp_write.txt"
            
            # Tạo file tạm trên máy tính
            local_temp_file = os.path.join(self.platform_info.temp_dir, "oiadb_temp_write.txt")
            with open(local_temp_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            # Đẩy file tạm lên thiết bị
            self.push(local_temp_file, temp_file)
            
            # Di chuyển file tạm đến vị trí đích
            result = self.adb.run(f"shell cat \"{temp_file}\" > \"{remote_path}\"")
            
            # Xóa file tạm
            self.adb.run(f"shell rm \"{temp_file}\"")
            os.remove(local_temp_file)
            
            return result
        except (ADBCommandError, FileOperationError, IOError) as e:
            raise FileOperationError("write", remote_path, "", str(e))
    
    def append(self, remote_path: str, content: str) -> str:
        """
        Thêm nội dung vào cuối file trên thiết bị.
        
        Args:
            remote_path: Đường dẫn file trên thiết bị
            content: Nội dung cần thêm
            
        Returns:
            Kết quả lệnh
            
        Raises:
            FileOperationError: Nếu thao tác thất bại
        """
        try:
            # Sử dụng đường dẫn tạm thời phù hợp với thiết bị
            device_temp_dir = self.platform_info.get_device_temp_dir()
            temp_file = f"{device_temp_dir}/oiadb_temp_append.txt"
            
            # Tạo file tạm trên máy tính
            local_temp_file = os.path.join(self.platform_info.temp_dir, "oiadb_temp_append.txt")
            with open(local_temp_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            # Đẩy file tạm lên thiết bị
            self.push(local_temp_file, temp_file)
            
            # Thêm nội dung vào file đích
            result = self.adb.run(f"shell cat \"{temp_file}\" >> \"{remote_path}\"")
            
            # Xóa file tạm
            self.adb.run(f"shell rm \"{temp_file}\"")
            os.remove(local_temp_file)
            
            return result
        except (ADBCommandError, FileOperationError, IOError) as e:
            raise FileOperationError("append", remote_path, "", str(e))
    
    def chmod(self, remote_path: str, mode: str) -> str:
        """
        Thay đổi quyền truy cập file hoặc thư mục trên thiết bị.
        
        Args:
            remote_path: Đường dẫn file hoặc thư mục
            mode: Quyền truy cập (ví dụ: "755")
            
        Returns:
            Kết quả lệnh
            
        Raises:
            FileOperationError: Nếu thao tác thất bại
        """
        try:
            return self.adb.run(f"shell chmod {mode} \"{remote_path}\"")
        except ADBCommandError as e:
            raise FileOperationError("chmod", remote_path, "", e.error_message)
    
    def get_size(self, remote_path: str) -> int:
        """
        Lấy kích thước file trên thiết bị.
        
        Args:
            remote_path: Đường dẫn file trên thiết bị
            
        Returns:
            Kích thước file (bytes)
            
        Raises:
            FileOperationError: Nếu thao tác thất bại
        """
        try:
            output = self.adb.run(f"shell stat -c %s \"{remote_path}\"")
            return int(output.strip())
        except (ADBCommandError, ValueError) as e:
            raise FileOperationError("get_size", remote_path, "", str(e))
    
    def get_free_space(self, mount_point: str = "/data") -> int:
        """
        Lấy dung lượng trống trên thiết bị.
        
        Args:
            mount_point: Điểm gắn kết (mount point)
            
        Returns:
            Dung lượng trống (bytes)
            
        Raises:
            FileOperationError: Nếu thao tác thất bại
        """
        try:
            # Sử dụng df để lấy thông tin dung lượng
            output = self.adb.run(f"shell df {mount_point}")
            lines = output.splitlines()
            
            if len(lines) < 2:
                raise FileOperationError("get_free_space", mount_point, "", "Invalid df output")
            
            # Phân tích dòng thứ hai (chứa thông tin)
            parts = lines[1].split()
            if len(parts) < 4:
                raise FileOperationError("get_free_space", mount_point, "", "Invalid df output format")
            
            # Lấy dung lượng trống (KB)
            free_kb = int(parts[3])
            return free_kb * 1024  # Chuyển đổi KB sang bytes
        except (ADBCommandError, ValueError, IndexError) as e:
            raise FileOperationError("get_free_space", mount_point, "", str(e))
