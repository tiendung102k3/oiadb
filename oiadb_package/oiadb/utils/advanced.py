"""
Tiện ích nâng cao cho thư viện My ADB Lib.
"""

import os
import time
import logging
import subprocess
import threading
from typing import List, Dict, Any, Optional, Union, Callable

# Thiết lập logging
logger = logging.getLogger('my_adb_lib')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class CommandResult:
    """Lớp đại diện cho kết quả của một lệnh ADB."""
    
    def __init__(self, command: str, stdout: str, stderr: str, return_code: int):
        self.command = command
        self.stdout = stdout
        self.stderr = stderr
        self.return_code = return_code
        self.success = return_code == 0
    
    def __str__(self) -> str:
        return self.stdout if self.success else self.stderr
    
    def __bool__(self) -> bool:
        return self.success


class AsyncCommandExecutor:
    """Lớp thực thi lệnh ADB bất đồng bộ."""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.results: Dict[str, CommandResult] = {}
        self.callbacks: Dict[str, Callable] = {}
        self._lock = threading.Lock()
    
    def execute(self, command_id: str, command: List[str], 
                callback: Optional[Callable] = None, 
                timeout: Optional[int] = None) -> None:
        """
        Thực thi lệnh bất đồng bộ.
        
        Args:
            command_id: ID duy nhất cho lệnh
            command: Danh sách các thành phần lệnh
            callback: Hàm callback khi lệnh hoàn thành
            timeout: Thời gian chờ tối đa (giây)
        """
        def _run_command():
            try:
                logger.debug(f"Executing command: {' '.join(command)}")
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    # text=True # Removed for Python 3.6 compatibility
                )
                
                with self._lock:
                    self.processes[command_id] = process
                
                try:
                    stdout_bytes, stderr_bytes = process.communicate(timeout=timeout)
                    stdout = stdout_bytes.decode(errors='ignore')
                    stderr = stderr_bytes.decode(errors='ignore')
                    result = CommandResult(
                        command=' '.join(command),
                        stdout=stdout,
                        stderr=stderr,
                        return_code=process.returncode
                    )
                    
                    with self._lock:
                        self.results[command_id] = result
                        if command_id in self.processes:
                            del self.processes[command_id]
                    
                    if callback:
                        callback(result)
                    
                except subprocess.TimeoutExpired:
                    with self._lock:
                        if command_id in self.processes:
                            self.processes[command_id].kill()
                            del self.processes[command_id]
                    
                    result = CommandResult(
                        command=' '.join(command),
                        stdout="",
                        stderr=f"Command timed out after {timeout} seconds",
                        return_code=-1
                    )
                    self.results[command_id] = result
                    
                    if callback:
                        callback(result)
            
            except Exception as e:
                logger.error(f"Error executing command {command_id}: {str(e)}")
                result = CommandResult(
                    command=' '.join(command),
                    stdout="",
                    stderr=str(e),
                    return_code=-1
                )
                
                with self._lock:
                    self.results[command_id] = result
                    if command_id in self.processes:
                        del self.processes[command_id]
                
                if callback:
                    callback(result)
        
        thread = threading.Thread(target=_run_command)
        thread.daemon = True
        thread.start()
    
    def get_result(self, command_id: str) -> Optional[CommandResult]:
        """
        Lấy kết quả của lệnh theo ID.
        
        Args:
            command_id: ID của lệnh
            
        Returns:
            CommandResult hoặc None nếu lệnh chưa hoàn thành
        """
        with self._lock:
            return self.results.get(command_id)
    
    def is_running(self, command_id: str) -> bool:
        """
        Kiểm tra xem lệnh có đang chạy không.
        
        Args:
            command_id: ID của lệnh
            
        Returns:
            True nếu lệnh đang chạy, False nếu không
        """
        with self._lock:
            return command_id in self.processes
    
    def kill(self, command_id: str) -> bool:
        """
        Hủy lệnh đang chạy.
        
        Args:
            command_id: ID của lệnh
            
        Returns:
            True nếu lệnh đã bị hủy thành công, False nếu không
        """
        with self._lock:
            if command_id in self.processes:
                try:
                    self.processes[command_id].kill()
                    del self.processes[command_id]
                    return True
                except:
                    return False
            return False


class DeviceMonitor:
    """Lớp theo dõi sự kiện thiết bị."""
    
    def __init__(self):
        self._running = False
        self._thread = None
        self._callbacks = []
        self._devices = set()
    
    def start(self):
        """Bắt đầu theo dõi thiết bị."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._monitor)
        self._thread.daemon = True
        self._thread.start()
    
    def stop(self):
        """Dừng theo dõi thiết bị."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
    
    def add_callback(self, callback):
        """
        Thêm callback khi có sự thay đổi thiết bị.
        
        Args:
            callback: Hàm callback(device_id, event_type)
                     event_type là 'connected' hoặc 'disconnected'
        """
        self._callbacks.append(callback)
    
    def _monitor(self):
        while self._running:
            try:
                # Lấy danh sách thiết bị hiện tại
                process = subprocess.run(
                    ["adb", "devices"], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    # text=True # Removed for Python 3.6 compatibility
                )
                stdout_str = process.stdout.decode(errors="ignore")
                
                if process.returncode != 0:
                    time.sleep(1)
                    continue
                
                # Phân tích danh sách thiết bị
                lines = stdout_str.strip().split("\n")[1:]
                current_devices = set()
                
                for line in lines:
                    if not line.strip():
                        continue
                    
                    parts = line.split('\t')
                    if len(parts) >= 2 and parts[1] == 'device':
                        current_devices.add(parts[0])
                
                # Kiểm tra thiết bị mới kết nối
                for device in current_devices:
                    if device not in self._devices:
                        for callback in self._callbacks:
                            try:
                                callback(device, 'connected')
                            except Exception as e:
                                logger.error(f"Error in device monitor callback: {str(e)}")
                
                # Kiểm tra thiết bị đã ngắt kết nối
                for device in self._devices:
                    if device not in current_devices:
                        for callback in self._callbacks:
                            try:
                                callback(device, 'disconnected')
                            except Exception as e:
                                logger.error(f"Error in device monitor callback: {str(e)}")
                
                self._devices = current_devices
            
            except Exception as e:
                logger.error(f"Error in device monitor: {str(e)}")
            
            time.sleep(1)


class ResultCache:
    """Lớp cache kết quả lệnh ADB."""
    
    def __init__(self, max_size=100, ttl=60):
        """
        Khởi tạo cache.
        
        Args:
            max_size: Kích thước tối đa của cache
            ttl: Thời gian sống của mỗi mục cache (giây)
        """
        self._cache = {}
        self._max_size = max_size
        self._ttl = ttl
        self._lock = threading.Lock()
    
    def get(self, key):
        """
        Lấy giá trị từ cache.
        
        Args:
            key: Khóa cache
            
        Returns:
            Giá trị cache hoặc None nếu không tìm thấy hoặc đã hết hạn
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            timestamp, value = self._cache[key]
            if time.time() - timestamp > self._ttl:
                del self._cache[key]
                return None
            
            return value
    
    def set(self, key, value):
        """
        Đặt giá trị vào cache.
        
        Args:
            key: Khóa cache
            value: Giá trị cần cache
        """
        with self._lock:
            # Nếu cache đầy, xóa mục cũ nhất
            if len(self._cache) >= self._max_size:
                oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][0])
                del self._cache[oldest_key]
            
            self._cache[key] = (time.time(), value)
    
    def clear(self):
        """Xóa toàn bộ cache."""
        with self._lock:
            self._cache.clear()
    
    def remove(self, key):
        """
        Xóa một mục khỏi cache.
        
        Args:
            key: Khóa cache cần xóa
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
