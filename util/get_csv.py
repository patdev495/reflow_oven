import os
import shutil

def copy_csv_xlsx(src_dir, dst_dir):
    """
    Duyệt đệ quy thư mục src_dir, tìm file .csv và .xlsx,
    sau đó copy sang thư mục dst_dir.
    """
    # Tạo thư mục đích nếu chưa có
    os.makedirs(dst_dir, exist_ok=True)

    # Duyệt toàn bộ cây thư mục
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.lower().endswith(('.csv', '.xlsx')):
                src_path = os.path.join(root, file)
                dst_path = os.path.join(dst_dir, file)

                # Nếu file trùng tên, thêm số để tránh ghi đè
                base, ext = os.path.splitext(file)
                counter = 1
                while os.path.exists(dst_path):
                    dst_path = os.path.join(dst_dir, f"{base}_{counter}{ext}")
                    counter += 1

                shutil.copy2(src_path, dst_path)
                print(f"✅ Copied: {src_path} → {dst_path}")

if __name__ == "__main__":
    # Ví dụ:
    src_folder = r"F:\dev\reflow\CHIEN\DO LÒ ME-B08-1F"       # thư mục gốc cần quét
    dst_folder = r"D:\DuLieu_CSV_XLSX"  # thư mục đích

    copy_csv_xlsx(src_folder, dst_folder)
