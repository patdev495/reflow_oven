import os
import shutil
import pandas as pd

# --- Cấu hình ---
excel_file = "filter_csv.xlsx"      # đường dẫn tới file Excel
source_root = r"F:\dev\reflow\data\CHIEN\DO LÒ ME-B08-1F"   # thư mục gốc
output_dir = "output"         # thư mục đích

# --- Đọc file Excel ---
df = pd.read_excel(excel_file)

# Đảm bảo thư mục đích tồn tại
os.makedirs(output_dir, exist_ok=True)

# --- Duyệt từng dòng ---
for index, row in df.iterrows():
    file_name = str(row['File Name']).strip()
    f1 = str(row['Folder Level 1']).strip() if not pd.isna(row['Folder Level 1']) else ''
    f2 = str(row['Folder Level 2']).strip() if not pd.isna(row['Folder Level 2']) else ''
    f3 = str(row['Folder Level 3']).strip() if not pd.isna(row['Folder Level 3']) else ''
    
    # Tạo đường dẫn đầy đủ tới file gốc
    src_path = os.path.join(source_root, f1, f2, f3, file_name)
    
    # Copy nếu file tồn tại
    if os.path.isfile(src_path):
        shutil.copy2(src_path, output_dir)
        print(f"✅ Copied: {src_path}")
    else:
        print(f"⚠️ File không tồn tại: {src_path}")

print("🎯 Hoàn tất copy!")
