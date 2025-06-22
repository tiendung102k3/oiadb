"""
Các lệnh tương tác với thiết bị Android dựa trên nhận diện hình ảnh.
"""

from typing import Optional, Tuple, List, Dict, Any, Union
import logging
import os

from ..exceptions import ADBCommandError
from ..utils.advanced import CommandResult
from ..utils.image_recognition import ImageRecognition
from ..utils.platform_utils import get_platform_info

logger = logging.getLogger('oiadb')

class ImageInteractionCommands:
    """
    Lớp chứa các lệnh tương tác với thiết bị Android dựa trên nhận diện hình ảnh.
    Hỗ trợ tìm kiếm và tương tác với hình ảnh trên nhiều loại màn hình với các điều kiện khác nhau
    (phân giải cao/thấp, hình ảnh nét/mờ/vỡ).
    """
    
    def __init__(self, adb_runner):
        """
        Khởi tạo đối tượng ImageInteractionCommands.
        
        Args:
            adb_runner: Đối tượng thực thi lệnh ADB
        """
        self.adb = adb_runner
        self.image_recognition = ImageRecognition(adb_runner)
        self.platform_info = get_platform_info()
    
    def find_image(self, template_path: str, threshold: float = 0.8, 
                  region: Optional[Tuple[int, int, int, int]] = None,
                  scale_range: Tuple[float, float] = (0.8, 1.2), scale_steps: int = 5,
                  rotation_range: Tuple[float, float] = (0, 0), rotation_steps: int = 1,
                  use_gray: bool = True, use_canny: bool = False) -> Optional[Tuple[int, int, float]]:
        """
        Tìm hình ảnh mẫu trên màn hình thiết bị.
        
        Args:
            template_path: Đường dẫn đến hình ảnh mẫu cần tìm
            threshold: Ngưỡng tương đồng (0.0 - 1.0), cao hơn = chính xác hơn
            region: Vùng tìm kiếm (x, y, width, height), None = toàn màn hình
            scale_range: Phạm vi tỷ lệ để tìm kiếm (min_scale, max_scale)
            scale_steps: Số bước tỷ lệ trong phạm vi
            rotation_range: Phạm vi góc xoay để tìm kiếm (min_angle, max_angle) tính bằng độ
            rotation_steps: Số bước góc xoay trong phạm vi
            use_gray: Sử dụng ảnh xám để tăng tốc độ tìm kiếm
            use_canny: Sử dụng phát hiện cạnh Canny để cải thiện kết quả với hình ảnh mờ
            
        Returns:
            Tuple (x, y, confidence) hoặc None nếu không tìm thấy
        """
        # Chuẩn hóa đường dẫn template
        template_path = self.platform_info.normalize_path(template_path)
        
        logger.debug(f"Tìm hình ảnh: {template_path}")
        return self.image_recognition.find_image(
            template_path=template_path,
            threshold=threshold,
            multiple=False,
            region=region,
            scale_range=scale_range,
            rotation_range=rotation_range,
            rotation_steps=rotation_steps,
            use_gray=use_gray,
            use_canny=use_canny
        )
    
    def find_all_images(self, template_path: str, threshold: float = 0.8, 
                       region: Optional[Tuple[int, int, int, int]] = None,
                       scale_range: Tuple[float, float] = (0.8, 1.2), scale_steps: int = 5,
                       use_gray: bool = True, use_canny: bool = False) -> List[Tuple[int, int, float]]:
        """
        Tìm tất cả các vị trí của hình ảnh mẫu trên màn hình.
        
        Args:
            template_path: Đường dẫn đến hình ảnh mẫu cần tìm
            threshold: Ngưỡng tương đồng (0.0 - 1.0)
            region: Vùng tìm kiếm (x, y, width, height), None = toàn màn hình
            scale_range: Phạm vi tỷ lệ để tìm kiếm (min_scale, max_scale)
            scale_steps: Số bước tỷ lệ trong phạm vi
            use_gray: Sử dụng ảnh xám để tăng tốc độ tìm kiếm
            use_canny: Sử dụng phát hiện cạnh Canny để cải thiện kết quả với hình ảnh mờ
            
        Returns:
            Danh sách các tuple (x, y, confidence) hoặc danh sách rỗng nếu không tìm thấy
        """
        # Chuẩn hóa đường dẫn template
        template_path = self.platform_info.normalize_path(template_path)
        
        logger.debug(f"Tìm tất cả hình ảnh: {template_path}")
        return self.image_recognition.find_all_images(
            template_path=template_path,
            threshold=threshold,
            region=region,
            scale_range=scale_range,
            scale_steps=scale_steps,
            use_gray=use_gray,
            use_canny=use_canny
        )
    
    def tap_image(self, template_path: str, threshold: float = 0.8, 
                 region: Optional[Tuple[int, int, int, int]] = None,
                 scale_range: Tuple[float, float] = (0.8, 1.2), scale_steps: int = 5,
                 use_gray: bool = True, use_canny: bool = False,
                 tap_offset: Tuple[int, int] = (0, 0)) -> bool:
        """
        Tìm hình ảnh trên màn hình và nhấp vào vị trí tìm thấy.
        
        Args:
            template_path: Đường dẫn đến hình ảnh mẫu cần tìm
            threshold: Ngưỡng tương đồng (0.0 - 1.0)
            region: Vùng tìm kiếm (x, y, width, height), None = toàn màn hình
            scale_range: Phạm vi tỷ lệ để tìm kiếm (min_scale, max_scale)
            scale_steps: Số bước tỷ lệ trong phạm vi
            use_gray: Sử dụng ảnh xám để tăng tốc độ tìm kiếm
            use_canny: Sử dụng phát hiện cạnh Canny để cải thiện kết quả với hình ảnh mờ
            tap_offset: Độ lệch (dx, dy) khi nhấp chuột so với tâm hình ảnh
            
        Returns:
            True nếu tìm thấy và nhấp thành công, False nếu không
        """
        # Chuẩn hóa đường dẫn template
        template_path = self.platform_info.normalize_path(template_path)
        
        logger.debug(f"Nhấp vào hình ảnh: {template_path}")
        return self.image_recognition.find_and_click(
            template_path=template_path,
            threshold=threshold,
            region=region,
            scale_range=scale_range,
            scale_steps=scale_steps,
            use_gray=use_gray,
            use_canny=use_canny,
            click_offset=tap_offset
        )
    
    def wait_and_tap_image(self, template_path: str, timeout: int = 10, interval: float = 0.5,
                          threshold: float = 0.8, region: Optional[Tuple[int, int, int, int]] = None,
                          scale_range: Tuple[float, float] = (0.8, 1.2), scale_steps: int = 5,
                          use_gray: bool = True, use_canny: bool = False,
                          tap_offset: Tuple[int, int] = (0, 0)) -> bool:
        """
        Đợi cho đến khi hình ảnh xuất hiện trên màn hình và nhấp vào vị trí đó.
        
        Args:
            template_path: Đường dẫn đến hình ảnh mẫu cần tìm
            timeout: Thời gian tối đa đợi (giây)
            interval: Khoảng thời gian giữa các lần tìm kiếm (giây)
            threshold: Ngưỡng tương đồng (0.0 - 1.0)
            region: Vùng tìm kiếm (x, y, width, height), None = toàn màn hình
            scale_range: Phạm vi tỷ lệ để tìm kiếm (min_scale, max_scale)
            scale_steps: Số bước tỷ lệ trong phạm vi
            use_gray: Sử dụng ảnh xám để tăng tốc độ tìm kiếm
            use_canny: Sử dụng phát hiện cạnh Canny để cải thiện kết quả với hình ảnh mờ
            tap_offset: Độ lệch (dx, dy) khi nhấp chuột so với tâm hình ảnh
            
        Returns:
            True nếu tìm thấy và nhấp thành công, False nếu hết thời gian chờ
        """
        # Chuẩn hóa đường dẫn template
        template_path = self.platform_info.normalize_path(template_path)
        
        logger.debug(f"Đợi và nhấp vào hình ảnh: {template_path}")
        return self.image_recognition.wait_and_click(
            template_path=template_path,
            timeout=timeout,
            interval=interval,
            threshold=threshold,
            region=region,
            scale_range=scale_range,
            scale_steps=scale_steps,
            use_gray=use_gray,
            use_canny=use_canny,
            click_offset=tap_offset
        )
    
    def save_screenshot(self, output_path: str) -> str:
        """
        Chụp ảnh màn hình và lưu vào file.
        
        Args:
            output_path: Đường dẫn lưu ảnh
            
        Returns:
            Đường dẫn đến file ảnh đã lưu
            
        Raises:
            ADBCommandError: Nếu lệnh thất bại
        """
        # Chuẩn hóa đường dẫn output
        output_path = self.platform_info.normalize_path(output_path)
        
        # Đảm bảo thư mục cha tồn tại
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        return self.adb.take_screenshot(output_path=output_path)
    
    def get_screenshot_as_bytes(self) -> bytes:
        """
        Chụp ảnh màn hình và trả về dưới dạng bytes.
        
        Returns:
            Dữ liệu ảnh dưới dạng bytes
            
        Raises:
            ADBCommandError: Nếu lệnh thất bại
        """
        return self.adb.take_screenshot(as_bytes=True)
