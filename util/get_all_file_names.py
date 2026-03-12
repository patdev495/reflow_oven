import os
import pandas as pd

def list_files_with_folders(src_dir, output_file):
    data = []

    for root, dirs, files in os.walk(src_dir):
        for file in files:
            # Lấy đường dẫn tương đối so với thư mục gốc
            rel_path = os.path.relpath(root, src_dir)
            
            # Nếu file nằm ngay trong thư mục gốc, không có thư mục cha
            if rel_path == ".":
                folders = []
            else:
                folders = rel_path.split(os.sep)

            # Ghi thông tin: tên file + các thư mục cha
            row = [file] + folders
            data.append(row)

    # Tìm số lượng cột lớn nhất (để tạo header tương ứng)
    max_depth = max(len(row) for row in data)

    # Tạo header động
    columns = ["File Name"] + [f"Folder Level {i}" for i in range(1, max_depth)]

    # Tạo DataFrame
    df = pd.DataFrame(data, columns=columns)

    # Ghi ra file CSV
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"✅ Đã quét xong {len(data)} file.")
    print(f"💾 Kết quả được lưu vào: {output_file}")


if __name__ == "__main__":
    src_folder = r"F:\dev\reflow\data\CHIEN\DO LÒ ME-B08-1F"           # thư mục gốc cần quét
    output_file = r"F:\dev\reflow\file_list.csv"  # file kết quả CSV

    list_files_with_folders(src_folder, output_file)
