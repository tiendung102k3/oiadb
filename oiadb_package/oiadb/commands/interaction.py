"""
Các lệnh tương tác với thiết bị Android.
"""

from typing import Optional, Tuple, List, Dict, Any
import logging

from ..exceptions import ADBCommandError
from ..utils.advanced import CommandResult

logger = logging.getLogger('my_adb_lib')

class InteractionCommands:
    """
    Lớp chứa các lệnh tương tác với thiết bị Android.
    """
    
    def __init__(self, adb_runner):
        """
        Khởi tạo đối tượng InteractionCommands.
        
        Args:
            adb_runner: Đối tượng thực thi lệnh ADB
        """
        self.adb = adb_runner
    
    def tap(self, x: int, y: int) -> str:
        """
        Tương tác nhấp chuột tại vị trí (x, y).
        
        Args:
            x: Tọa độ X
            y: Tọa độ Y
            
        Returns:
            Kết quả lệnh
        """
        logger.debug(f"Tapping at position ({x}, {y})")
        return self.adb.run(f"shell input tap {x} {y}")
    
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> str:
        """
        Tương tác vuốt từ (x1, y1) tới (x2, y2) trong thời gian duration (ms).
        
        Args:
            x1: Tọa độ X bắt đầu
            y1: Tọa độ Y bắt đầu
            x2: Tọa độ X kết thúc
            y2: Tọa độ Y kết thúc
            duration: Thời gian vuốt (ms)
            
        Returns:
            Kết quả lệnh
        """
        logger.debug(f"Swiping from ({x1}, {y1}) to ({x2}, {y2}) with duration {duration}ms")
        return self.adb.run(f"shell input swipe {x1} {y1} {x2} {y2} {duration}")
    
    def text_input(self, text: str) -> str:
        """
        Nhập văn bản vào thiết bị Android.
        
        Args:
            text: Văn bản cần nhập
            
        Returns:
            Kết quả lệnh
        """
        # Thay thế các ký tự đặc biệt
        text = text.replace(" ", "%s").replace("'", "\\'").replace("\"", "\\\"")
        logger.debug(f"Inputting text: {text}")
        return self.adb.run(f"shell input text '{text}'")
    
    def key_event(self, key_code: int) -> str:
        """
        Gửi một sự kiện phím (key event) cho thiết bị.
        
        Args:
            key_code: Mã phím
            
        Returns:
            Kết quả lệnh
        """
        logger.debug(f"Sending key event: {key_code}")
        return self.adb.run(f"shell input keyevent {key_code}")
    
    def back(self) -> str:
        """
        Nhấn nút back.
        
        Returns:
            Kết quả lệnh
        """
        logger.debug("Pressing back button")
        return self.key_event(4)
    
    def home(self) -> str:
        """
        Nhấn nút home.
        
        Returns:
            Kết quả lệnh
        """
        logger.debug("Pressing home button")
        return self.key_event(3)
    
    def menu(self) -> str:
        """
        Nhấn nút menu.
        
        Returns:
            Kết quả lệnh
        """
        logger.debug("Pressing menu button")
        return self.key_event(82)
    
    def power(self) -> str:
        """
        Nhấn nút power.
        
        Returns:
            Kết quả lệnh
        """
        logger.debug("Pressing power button")
        return self.key_event(26)
    
    def volume_up(self) -> str:
        """
        Nhấn nút tăng âm lượng.
        
        Returns:
            Kết quả lệnh
        """
        logger.debug("Pressing volume up button")
        return self.key_event(24)
    
    def volume_down(self) -> str:
        """
        Nhấn nút giảm âm lượng.
        
        Returns:
            Kết quả lệnh
        """
        logger.debug("Pressing volume down button")
        return self.key_event(25)
    
    def enter(self) -> str:
        """
        Nhấn phím Enter.
        
        Returns:
            Kết quả lệnh
        """
        logger.debug("Pressing enter key")
        return self.key_event(66)
    
    def tab(self) -> str:
        """
        Nhấn phím Tab.
        
        Returns:
            Kết quả lệnh
        """
        logger.debug("Pressing tab key")
        return self.key_event(61)
    
    def delete(self) -> str:
        """
        Nhấn phím Delete.
        
        Returns:
            Kết quả lệnh
        """
        logger.debug("Pressing delete key")
        return self.key_event(67)
    
    def recent_apps(self) -> str:
        """
        Hiển thị các ứng dụng gần đây.
        
        Returns:
            Kết quả lệnh
        """
        logger.debug("Showing recent apps")
        return self.key_event(187)
    
    def long_press(self, x: int, y: int, duration: int = 1000) -> str:
        """
        Nhấn giữ tại vị trí (x, y) trong thời gian duration (ms).
        
        Args:
            x: Tọa độ X
            y: Tọa độ Y
            duration: Thời gian nhấn giữ (ms)
            
        Returns:
            Kết quả lệnh
        """
        logger.debug(f"Long pressing at position ({x}, {y}) for {duration}ms")
        return self.swipe(x, y, x, y, duration)
    
    def pinch(self, x1: int, y1: int, x2: int, y2: int, 
             x3: int, y3: int, x4: int, y4: int, 
             duration: int = 500) -> Tuple[str, str]:
        """
        Thực hiện thao tác pinch (thu nhỏ/phóng to).
        
        Args:
            x1, y1: Tọa độ bắt đầu của ngón tay 1
            x2, y2: Tọa độ kết thúc của ngón tay 1
            x3, y3: Tọa độ bắt đầu của ngón tay 2
            x4, y4: Tọa độ kết thúc của ngón tay 2
            duration: Thời gian thực hiện (ms)
            
        Returns:
            Tuple chứa kết quả của hai lệnh swipe
        """
        logger.debug(f"Performing pinch gesture from ({x1}, {y1})->({x2}, {y2}) and ({x3}, {y3})->({x4}, {y4})")
        result1 = self.adb.run(f"shell input swipe {x1} {y1} {x2} {y2} {duration}")
        result2 = self.adb.run(f"shell input swipe {x3} {y3} {x4} {y4} {duration}")
        return (result1, result2)
    
    def zoom_in(self, center_x: int, center_y: int, distance: int = 200, 
               duration: int = 500) -> Tuple[str, str]:
        """
        Thực hiện thao tác phóng to (zoom in).
        
        Args:
            center_x: Tọa độ X trung tâm
            center_y: Tọa độ Y trung tâm
            distance: Khoảng cách di chuyển
            duration: Thời gian thực hiện (ms)
            
        Returns:
            Tuple chứa kết quả của hai lệnh swipe
        """
        logger.debug(f"Performing zoom in gesture at center ({center_x}, {center_y})")
        half_distance = distance // 2
        return self.pinch(
            center_x - half_distance, center_y - half_distance, center_x, center_y,
            center_x + half_distance, center_y + half_distance, center_x, center_y,
            duration
        )
    
    def zoom_out(self, center_x: int, center_y: int, distance: int = 200, 
                duration: int = 500) -> Tuple[str, str]:
        """
        Thực hiện thao tác thu nhỏ (zoom out).
        
        Args:
            center_x: Tọa độ X trung tâm
            center_y: Tọa độ Y trung tâm
            distance: Khoảng cách di chuyển
            duration: Thời gian thực hiện (ms)
            
        Returns:
            Tuple chứa kết quả của hai lệnh swipe
        """
        logger.debug(f"Performing zoom out gesture at center ({center_x}, {center_y})")
        half_distance = distance // 2
        return self.pinch(
            center_x, center_y, center_x - half_distance, center_y - half_distance,
            center_x, center_y, center_x + half_distance, center_y + half_distance,
            duration
        )
    
    def drag(self, x1: int, y1: int, x2: int, y2: int, duration: int = 1000) -> str:
        """
        Thực hiện thao tác kéo (drag) từ (x1, y1) đến (x2, y2).
        
        Args:
            x1: Tọa độ X bắt đầu
            y1: Tọa độ Y bắt đầu
            x2: Tọa độ X kết thúc
            y2: Tọa độ Y kết thúc
            duration: Thời gian thực hiện (ms)
            
        Returns:
            Kết quả lệnh
        """
        logger.debug(f"Dragging from ({x1}, {y1}) to ({x2}, {y2})")
        return self.swipe(x1, y1, x2, y2, duration)
    
    def scroll_up(self, distance: int = 500, duration: int = 500) -> str:
        """
        Cuộn lên trên.
        
        Args:
            distance: Khoảng cách cuộn
            duration: Thời gian thực hiện (ms)
            
        Returns:
            Kết quả lệnh
        """
        # Lấy kích thước màn hình
        try:
            size = self.adb.get_screen_size()
            width, height = size["width"], size["height"]
            
            if width == 0 or height == 0:
                # Sử dụng giá trị mặc định nếu không lấy được kích thước màn hình
                width, height = 1080, 1920
            
            center_x = width // 2
            start_y = height // 2
            end_y = start_y - distance
            
            logger.debug(f"Scrolling up by {distance} pixels")
            return self.swipe(center_x, start_y, center_x, end_y, duration)
        
        except Exception as e:
            logger.error(f"Error in scroll_up: {str(e)}")
            # Sử dụng giá trị mặc định
            return self.swipe(500, 1000, 500, 500, duration)
    
    def scroll_down(self, distance: int = 500, duration: int = 500) -> str:
        """
        Cuộn xuống dưới.
        
        Args:
            distance: Khoảng cách cuộn
            duration: Thời gian thực hiện (ms)
            
        Returns:
            Kết quả lệnh
        """
        # Lấy kích thước màn hình
        try:
            size = self.adb.get_screen_size()
            width, height = size["width"], size["height"]
            
            if width == 0 or height == 0:
                # Sử dụng giá trị mặc định nếu không lấy được kích thước màn hình
                width, height = 1080, 1920
            
            center_x = width // 2
            start_y = height // 2
            end_y = start_y + distance
            
            logger.debug(f"Scrolling down by {distance} pixels")
            return self.swipe(center_x, start_y, center_x, end_y, duration)
        
        except Exception as e:
            logger.error(f"Error in scroll_down: {str(e)}")
            # Sử dụng giá trị mặc định
            return self.swipe(500, 500, 500, 1000, duration)
    
    def scroll_left(self, distance: int = 500, duration: int = 500) -> str:
        """
        Cuộn sang trái.
        
        Args:
            distance: Khoảng cách cuộn
            duration: Thời gian thực hiện (ms)
            
        Returns:
            Kết quả lệnh
        """
        # Lấy kích thước màn hình
        try:
            size = self.adb.get_screen_size()
            width, height = size["width"], size["height"]
            
            if width == 0 or height == 0:
                # Sử dụng giá trị mặc định nếu không lấy được kích thước màn hình
                width, height = 1080, 1920
            
            center_y = height // 2
            start_x = width // 2
            end_x = start_x - distance
            
            logger.debug(f"Scrolling left by {distance} pixels")
            return self.swipe(start_x, center_y, end_x, center_y, duration)
        
        except Exception as e:
            logger.error(f"Error in scroll_left: {str(e)}")
            # Sử dụng giá trị mặc định
            return self.swipe(800, 500, 300, 500, duration)
    
    def scroll_right(self, distance: int = 500, duration: int = 500) -> str:
        """
        Cuộn sang phải.
        
        Args:
            distance: Khoảng cách cuộn
            duration: Thời gian thực hiện (ms)
            
        Returns:
            Kết quả lệnh
        """
        # Lấy kích thước màn hình
        try:
            size = self.adb.get_screen_size()
            width, height = size["width"], size["height"]
            
            if width == 0 or height == 0:
                # Sử dụng giá trị mặc định nếu không lấy được kích thước màn hình
                width, height = 1080, 1920
            
            center_y = height // 2
            start_x = width // 2
            end_x = start_x + distance
            
            logger.debug(f"Scrolling right by {distance} pixels")
            return self.swipe(start_x, center_y, end_x, center_y, duration)
        
        except Exception as e:
            logger.error(f"Error in scroll_right: {str(e)}")
            # Sử dụng giá trị mặc định
            return self.swipe(300, 500, 800, 500, duration)
    
    def type_keycode_sequence(self, keycodes: List[int]) -> List[str]:
        """
        Nhập một chuỗi mã phím.
        
        Args:
            keycodes: Danh sách các mã phím
            
        Returns:
            Danh sách kết quả lệnh
        """
        logger.debug(f"Typing keycode sequence: {keycodes}")
        results = []
        for keycode in keycodes:
            results.append(self.key_event(keycode))
        return results
    
    def wake_up(self) -> str:
        """
        Đánh thức thiết bị.
        
        Returns:
            Kết quả lệnh
        """
        logger.debug("Waking up device")
        return self.adb.run("shell input keyevent KEYCODE_WAKEUP")
    
    def sleep(self) -> str:
        """
        Đưa thiết bị vào chế độ ngủ.
        
        Returns:
            Kết quả lệnh
        """
        logger.debug("Putting device to sleep")
        return self.adb.run("shell input keyevent KEYCODE_SLEEP")
    
    def unlock(self, pattern: Optional[List[int]] = None, pin: Optional[str] = None) -> str:
        """
        Mở khóa thiết bị.
        
        Args:
            pattern: Mẫu mở khóa (danh sách các điểm từ 1-9)
            pin: Mã PIN mở khóa
            
        Returns:
            Kết quả lệnh
        """
        logger.debug("Unlocking device")
        
        # Đánh thức thiết bị
        self.wake_up()
        
        # Vuốt lên để mở màn hình khóa
        try:
            size = self.adb.get_screen_size()
            width, height = size["width"], size["height"]
            
            if width == 0 or height == 0:
                # Sử dụng giá trị mặc định nếu không lấy được kích thước màn hình
                width, height = 1080, 1920
            
            center_x = width // 2
            self.swipe(center_x, height * 3 // 4, center_x, height // 4, 300)
        
        except Exception as e:
            logger.error(f"Error in unlock swipe: {str(e)}")
            # Sử dụng giá trị mặc định
            self.swipe(500, 1500, 500, 500, 300)
        
        # Nếu có mẫu mở khóa
        if pattern:
            # Tính toán vị trí các điểm
            try:
                size = self.adb.get_screen_size()
                width, height = size["width"], size["height"]
                
                if width == 0 or height == 0:
                    # Sử dụng giá trị mặc định nếu không lấy được kích thước màn hình
                    width, height = 1080, 1920
                
                # Kích thước và vị trí của lưới mở khóa
                grid_size = min(width, height) * 0.7
                grid_left = (width - grid_size) / 2
                grid_top = (height - grid_size) / 2
                cell_size = grid_size / 3
                
                # Tính toán tọa độ các điểm
                points = []
                for p in pattern:
                    if p < 1 or p > 9:
                        continue
                    
                    row = (p - 1) // 3
                    col = (p - 1) % 3
                    
                    x = grid_left + col * cell_size + cell_size / 2
                    y = grid_top + row * cell_size + cell_size / 2
                    
                    points.append((int(x), int(y)))
                
                # Tạo lệnh vuốt qua các điểm
                if len(points) >= 2:
                    cmd = f"shell input swipe {points[0][0]} {points[0][1]}"
                    for x, y in points[1:]:
                        cmd += f" {x} {y}"
                    cmd += " 1000"
                    
                    return self.adb.run(cmd)
            
            except Exception as e:
                logger.error(f"Error in pattern unlock: {str(e)}")
        
        # Nếu có mã PIN
        elif pin:
            # Đợi một chút để màn hình PIN hiển thị
            import time
            time.sleep(1)
            
            # Nhập từng số trong PIN
            for digit in pin:
                self.key_event(int(digit) + 7)  # KEYCODE_0 = 7, KEYCODE_1 = 8, ...
            
            # Nhấn Enter để xác nhận
            return self.enter()
        
        return "Unlock attempted"
