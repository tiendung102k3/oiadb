"""
Ví dụ sử dụng chức năng nhận diện hình ảnh trong thư viện OIADB.
"""

import os
import time
from oiadb import MyADB
from commands.image_interaction import ImageInteractionCommands

def example_find_and_click_image():
    """
    Ví dụ tìm và nhấp vào hình ảnh trên màn hình thiết bị.
    """
    # Khởi tạo ADB
    adb = MyADB()
    
    # Khởi tạo đối tượng tương tác hình ảnh
    image_interaction = ImageInteractionCommands(adb)
    
    # Đường dẫn đến thư mục chứa hình ảnh mẫu
    template_dir = "./templates"
    os.makedirs(template_dir, exist_ok=True)
    
    # Chụp ảnh màn hình để sử dụng làm mẫu
    print("Chụp ảnh màn hình để tạo mẫu...")
    adb.take_screenshot(f"{template_dir}/screenshot.png")
    
    # Giả sử bạn đã có hình ảnh biểu tượng ứng dụng
    app_icon_path = f"{template_dir}/app_icon.png"
    
    # Tìm và nhấp vào biểu tượng ứng dụng
    print("Tìm và nhấp vào biểu tượng ứng dụng...")
    result = image_interaction.tap_image(
        template_path=app_icon_path,
        threshold=0.8,  # Ngưỡng tương đồng
        scale_range=(0.8, 1.2),  # Tìm với nhiều tỷ lệ khác nhau
        scale_steps=5,  # Số bước tỷ lệ
        use_gray=True,  # Sử dụng ảnh xám để tăng tốc độ
        use_canny=False  # Không sử dụng phát hiện cạnh Canny
    )
    
    if result:
        print("Đã tìm thấy và nhấp vào biểu tượng ứng dụng!")
    else:
        print("Không tìm thấy biểu tượng ứng dụng.")

def example_wait_for_image():
    """
    Ví dụ đợi hình ảnh xuất hiện trên màn hình thiết bị.
    """
    # Khởi tạo ADB
    adb = MyADB()
    
    # Khởi tạo đối tượng tương tác hình ảnh
    image_interaction = ImageInteractionCommands(adb)
    
    # Đường dẫn đến hình ảnh mẫu
    loading_icon_path = "./templates/loading_icon.png"
    
    # Đợi biểu tượng tải xuất hiện
    print("Đợi biểu tượng tải xuất hiện...")
    result = image_interaction.wait_for_image(
        template_path=loading_icon_path,
        timeout=10,  # Thời gian tối đa đợi (giây)
        interval=0.5,  # Khoảng thời gian giữa các lần tìm kiếm (giây)
        threshold=0.7  # Ngưỡng tương đồng thấp hơn cho hình ảnh có thể mờ
    )
    
    if result:
        print(f"Đã tìm thấy biểu tượng tải tại vị trí {result[0]}, {result[1]} với độ tương đồng {result[2]:.2f}")
        
        # Đợi biểu tượng tải biến mất
        print("Đợi biểu tượng tải biến mất...")
        disappeared = image_interaction.wait_until_image_disappears(
            template_path=loading_icon_path,
            timeout=30,
            interval=1.0,
            threshold=0.7
        )
        
        if disappeared:
            print("Biểu tượng tải đã biến mất, trang đã tải xong!")
        else:
            print("Biểu tượng tải vẫn còn hiển thị sau thời gian chờ.")
    else:
        print("Không tìm thấy biểu tượng tải trong thời gian chờ.")

def example_find_multiple_images():
    """
    Ví dụ tìm nhiều hình ảnh trên màn hình thiết bị.
    """
    # Khởi tạo ADB
    adb = MyADB()
    
    # Khởi tạo đối tượng tương tác hình ảnh
    image_interaction = ImageInteractionCommands(adb)
    
    # Đường dẫn đến hình ảnh mẫu
    button_template_path = "./templates/button.png"
    
    # Tìm tất cả các nút trên màn hình
    print("Tìm tất cả các nút trên màn hình...")
    results = image_interaction.find_all_images(
        template_path=button_template_path,
        threshold=0.8,
        scale_range=(0.8, 1.2),
        scale_steps=5
    )
    
    if results:
        print(f"Đã tìm thấy {len(results)} nút trên màn hình:")
        for i, (x, y, confidence) in enumerate(results):
            print(f"  Nút {i+1}: Vị trí ({x}, {y}), Độ tương đồng: {confidence:.2f}")
        
        # Nhấp vào tất cả các nút
        print("Nhấp vào tất cả các nút...")
        count = image_interaction.tap_all_images(
            template_path=button_template_path,
            threshold=0.8,
            tap_delay=1.0  # Chờ 1 giây giữa các lần nhấp
        )
        print(f"Đã nhấp vào {count} nút.")
    else:
        print("Không tìm thấy nút nào trên màn hình.")

def example_drag_between_images():
    """
    Ví dụ kéo từ hình ảnh này đến hình ảnh khác.
    """
    # Khởi tạo ADB
    adb = MyADB()
    
    # Khởi tạo đối tượng tương tác hình ảnh
    image_interaction = ImageInteractionCommands(adb)
    
    # Đường dẫn đến hình ảnh mẫu
    source_image_path = "./templates/source_item.png"
    target_image_path = "./templates/target_area.png"
    
    # Kéo từ mục nguồn đến khu vực đích
    print("Kéo từ mục nguồn đến khu vực đích...")
    result = image_interaction.drag_image_to_image(
        source_template_path=source_image_path,
        target_template_path=target_image_path,
        duration=800,  # Thời gian kéo (ms)
        threshold=0.8,
        scale_range=(0.8, 1.2),
        scale_steps=5
    )
    
    if result:
        print("Đã kéo thành công từ mục nguồn đến khu vực đích!")
    else:
        print("Không thể kéo vì không tìm thấy một hoặc cả hai hình ảnh.")

def example_handle_different_screen_conditions():
    """
    Ví dụ xử lý các điều kiện màn hình khác nhau (phân giải, nét, mờ, vỡ).
    """
    # Khởi tạo ADB
    adb = MyADB()
    
    # Khởi tạo đối tượng tương tác hình ảnh
    image_interaction = ImageInteractionCommands(adb)
    
    # Đường dẫn đến hình ảnh mẫu
    button_template_path = "./templates/button.png"
    
    print("Tìm hình ảnh với các cài đặt khác nhau cho các điều kiện màn hình khác nhau...")
    
    # 1. Màn hình phân giải cao
    print("\n1. Tìm trên màn hình phân giải cao (tỷ lệ lớn):")
    result_high_res = image_interaction.find_image(
        template_path=button_template_path,
        threshold=0.8,
        scale_range=(1.0, 1.5),  # Tỷ lệ lớn hơn cho màn hình phân giải cao
        scale_steps=5
    )
    if result_high_res:
        print(f"  Đã tìm thấy tại ({result_high_res[0]}, {result_high_res[1]}) với độ tương đồng {result_high_res[2]:.2f}")
    else:
        print("  Không tìm thấy trên màn hình phân giải cao.")
    
    # 2. Màn hình phân giải thấp
    print("\n2. Tìm trên màn hình phân giải thấp (tỷ lệ nhỏ):")
    result_low_res = image_interaction.find_image(
        template_path=button_template_path,
        threshold=0.8,
        scale_range=(0.5, 1.0),  # Tỷ lệ nhỏ hơn cho màn hình phân giải thấp
        scale_steps=5
    )
    if result_low_res:
        print(f"  Đã tìm thấy tại ({result_low_res[0]}, {result_low_res[1]}) với độ tương đồng {result_low_res[2]:.2f}")
    else:
        print("  Không tìm thấy trên màn hình phân giải thấp.")
    
    # 3. Hình ảnh mờ
    print("\n3. Tìm hình ảnh mờ (sử dụng phát hiện cạnh Canny):")
    result_blurry = image_interaction.find_image(
        template_path=button_template_path,
        threshold=0.7,  # Ngưỡng thấp hơn cho hình ảnh mờ
        scale_range=(0.8, 1.2),
        scale_steps=5,
        use_canny=True  # Sử dụng phát hiện cạnh Canny cho hình ảnh mờ
    )
    if result_blurry:
        print(f"  Đã tìm thấy tại ({result_blurry[0]}, {result_blurry[1]}) với độ tương đồng {result_blurry[2]:.2f}")
    else:
        print("  Không tìm thấy hình ảnh mờ.")
    
    # 4. Hình ảnh xoay
    print("\n4. Tìm hình ảnh xoay:")
    result_rotated = image_interaction.find_image(
        template_path=button_template_path,
        threshold=0.7,
        scale_range=(0.8, 1.2),
        scale_steps=3,
        rotation_range=(-15, 15),  # Tìm với góc xoay từ -15 đến 15 độ
        rotation_steps=5
    )
    if result_rotated:
        print(f"  Đã tìm thấy tại ({result_rotated[0]}, {result_rotated[1]}) với độ tương đồng {result_rotated[2]:.2f}")
    else:
        print("  Không tìm thấy hình ảnh xoay.")

def example_complex_workflow():
    """
    Ví dụ quy trình phức tạp sử dụng nhiều chức năng nhận diện hình ảnh.
    """
    # Khởi tạo ADB
    adb = MyADB()
    
    # Khởi tạo đối tượng tương tác hình ảnh
    image_interaction = ImageInteractionCommands(adb)
    
    # Đường dẫn đến các hình ảnh mẫu
    app_icon_path = "./templates/app_icon.png"
    login_button_path = "./templates/login_button.png"
    username_field_path = "./templates/username_field.png"
    password_field_path = "./templates/password_field.png"
    submit_button_path = "./templates/submit_button.png"
    loading_icon_path = "./templates/loading_icon.png"
    home_screen_path = "./templates/home_screen.png"
    
    print("Bắt đầu quy trình đăng nhập tự động...")
    
    # 1. Mở ứng dụng
    print("1. Tìm và nhấp vào biểu tượng ứng dụng...")
    if not image_interaction.tap_image(app_icon_path, threshold=0.8):
        print("Không tìm thấy biểu tượng ứng dụng. Dừng quy trình.")
        return
    
    # 2. Đợi màn hình đăng nhập xuất hiện
    print("2. Đợi màn hình đăng nhập xuất hiện...")
    if not image_interaction.wait_for_image(login_button_path, timeout=10, threshold=0.8):
        print("Không tìm thấy màn hình đăng nhập. Dừng quy trình.")
        return
    
    # 3. Nhập tên người dùng
    print("3. Nhập tên người dùng...")
    if image_interaction.tap_image(username_field_path, threshold=0.8):
        # Nhập tên người dùng
        adb.run("shell input text 'testuser'")
    else:
        print("Không tìm thấy trường tên người dùng. Dừng quy trình.")
        return
    
    # 4. Nhập mật khẩu
    print("4. Nhập mật khẩu...")
    if image_interaction.tap_image(password_field_path, threshold=0.8):
        # Nhập mật khẩu
        adb.run("shell input text 'password123'")
    else:
        print("Không tìm thấy trường mật khẩu. Dừng quy trình.")
        return
    
    # 5. Nhấp vào nút đăng nhập
    print("5. Nhấp vào nút đăng nhập...")
    if not image_interaction.tap_image(submit_button_path, threshold=0.8):
        print("Không tìm thấy nút đăng nhập. Dừng quy trình.")
        return
    
    # 6. Đợi biểu tượng tải xuất hiện và biến mất
    print("6. Đợi quá trình đăng nhập hoàn tất...")
    if image_interaction.wait_for_image(loading_icon_path, timeout=5, threshold=0.7):
        # Đợi biểu tượng tải biến mất
        if not image_interaction.wait_until_image_disappears(loading_icon_path, timeout=30, threshold=0.7):
            print("Quá trình đăng nhập mất quá nhiều thời gian. Dừng quy trình.")
            return
    
    # 7. Xác minh đã đăng nhập thành công
    print("7. Xác minh đã đăng nhập thành công...")
    if image_interaction.is_image_present(home_screen_path, threshold=0.8):
        print("Đăng nhập thành công! Đã vào màn hình chính.")
    else:
        print("Không thể xác minh đăng nhập thành công.")

if __name__ == "__main__":
    print("Ví dụ sử dụng chức năng nhận diện hình ảnh trong OIADB")
    print("=" * 60)
    
    # Chạy các ví dụ
    print("\n[Ví dụ 1: Tìm và nhấp vào hình ảnh]")
    example_find_and_click_image()
    
    print("\n[Ví dụ 2: Đợi hình ảnh xuất hiện]")
    example_wait_for_image()
    
    print("\n[Ví dụ 3: Tìm nhiều hình ảnh]")
    example_find_multiple_images()
    
    print("\n[Ví dụ 4: Kéo giữa các hình ảnh]")
    example_drag_between_images()
    
    print("\n[Ví dụ 5: Xử lý các điều kiện màn hình khác nhau]")
    example_handle_different_screen_conditions()
    
    print("\n[Ví dụ 6: Quy trình phức tạp]")
    example_complex_workflow()
