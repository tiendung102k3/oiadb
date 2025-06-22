# My ADB Lib - Ví dụ sử dụng

Dưới đây là một số ví dụ về cách sử dụng thư viện My ADB Lib.

## Kết nối thiết bị

```python
from my_adb_lib import MyADB

# Kết nối với thiết bị mặc định
adb = MyADB()

# Kết nối với thiết bị cụ thể
adb = MyADB(device_id="emulator-5554")

# Kết nối qua mạng không dây
adb = MyADB()
adb.connect_wireless("192.168.1.100", 5555)

# Ghép nối thiết bị không dây với mã ghép nối (Android 11+)
adb.wireless_pair("192.168.1.100", 5555, "123456")
```

## Quản lý ứng dụng

```python
from my_adb_lib import MyADB

adb = MyADB()

# Cài đặt ứng dụng
adb.install_app("/path/to/app.apk", replace=True, grant_permissions=True)

# Gỡ cài đặt ứng dụng
adb.uninstall_app("com.example.app")

# Khởi động ứng dụng
adb.start_app("com.example.app")

# Dừng ứng dụng
adb.stop_app("com.example.app")

# Xóa dữ liệu ứng dụng
adb.clear_app_data("com.example.app")

# Kiểm tra phiên bản ứng dụng
version = adb.get_app_version("com.example.app")
print(f"Phiên bản: {version}")

# Kiểm tra ứng dụng đã cài đặt chưa
if adb.is_app_installed("com.example.app"):
    print("Ứng dụng đã được cài đặt")
else:
    print("Ứng dụng chưa được cài đặt")
```

## Tương tác với thiết bị

```python
from my_adb_lib import MyADB

adb = MyADB()

# Nhấn vào tọa độ
adb.tap(500, 500)

# Vuốt màn hình
adb.swipe(100, 500, 600, 500)

# Nhập văn bản
adb.input_text("Hello World")

# Nhấn phím
adb.press_back()
adb.press_home()
adb.press_power()

# Chụp ảnh màn hình
adb.take_screenshot("/path/to/screenshot.png")

# Quay video màn hình
command_id = adb.record_screen("/path/to/video.mp4", time_limit=10)

# Đợi quay video hoàn thành
while adb.is_async_running(command_id):
    print("Đang quay video...")
    import time
    time.sleep(1)
```

## Quản lý file

```python
from my_adb_lib.commands import file_ops

adb = MyADB()
files = file_ops.FileCommands(adb)

# Đẩy file lên thiết bị
files.push("/path/on/computer", "/sdcard/file.txt")

# Lấy file từ thiết bị
files.pull("/sdcard/file.txt", "/path/on/computer")

# Liệt kê file
file_list = files.ls("/sdcard")
for file in file_list:
    print(file)

# Đọc nội dung file
content = files.cat("/sdcard/file.txt")
print(content)

# Ghi nội dung vào file
files.write_file("/sdcard/new_file.txt", "Hello World")

# Kiểm tra file tồn tại
if files.file_exists("/sdcard/file.txt"):
    print("File tồn tại")
```

## Lấy thông tin thiết bị

```python
from my_adb_lib import MyADB
from my_adb_lib.commands import device_info

adb = MyADB()
device = device_info.DeviceCommands(adb)

# Lấy thông tin cơ bản
print(f"Android version: {device.get_android_version()}")
print(f"SDK version: {device.get_sdk_version()}")
print(f"Model: {device.get_device_model()}")
print(f"Manufacturer: {device.get_device_manufacturer()}")

# Lấy kích thước màn hình
width, height = device.screen_size()
print(f"Screen size: {width}x{height}")

# Lấy thông tin pin
battery = device.battery()
print(f"Battery level: {battery.get('level')}%")
print(f"Battery status: {battery.get('status')}")

# Lấy thông tin hệ thống
system_info = device.get_system_info()
print(f"CPU: {system_info['cpu']}")
print(f"Memory: {system_info['memory']}")
print(f"Disk: {system_info['disk']}")
print(f"Network: {system_info['network']}")
```

## Sử dụng bất đồng bộ

```python
from my_adb_lib import MyADB

adb = MyADB()

# Định nghĩa callback
def on_command_complete(result):
    if result.success:
        print(f"Lệnh hoàn thành thành công: {result.stdout}")
    else:
        print(f"Lệnh thất bại: {result.stderr}")

# Thực thi lệnh bất đồng bộ
command_id = adb.run_async("shell ls -la /sdcard", callback=on_command_complete)

# Kiểm tra trạng thái
if adb.is_async_running(command_id):
    print("Lệnh đang chạy...")

# Lấy kết quả (nếu đã hoàn thành)
result = adb.get_async_result(command_id)
if result:
    print(f"Kết quả: {result}")

# Hủy lệnh đang chạy
adb.kill_async(command_id)
```

## Theo dõi thiết bị

```python
from my_adb_lib import MyADB

adb = MyADB()

# Lấy đối tượng theo dõi thiết bị
monitor = adb.get_device_monitor()

# Định nghĩa callback
def on_device_change(device_id, event_type):
    print(f"Thiết bị {device_id}: {event_type}")

# Thêm callback
monitor.add_callback(on_device_change)

# Bắt đầu theo dõi
monitor.start()

# Dừng theo dõi khi không cần nữa
# monitor.stop()
```
