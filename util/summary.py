#!/usr/bin/env python3
# summary.py
import os
import glob
import chardet
import pandas as pd
import re

# =======================
# CẤU HÌNH
# =======================
source_dir = r"C:\Users\AKTF\Downloads\GỬI ANH ĐÀ EXCEL PROFILE\GỬI ANH ĐÀ EXCEL PROFILE"           # thư mục chứa file CSV
output_file = r"summary11.csv"     # file tổng hợp

# Cột cần tìm
keywords_first = ["Product Name", "Processing Name", "Stove Name"]
temp_zones_en = [f"Area {i}" for i in range(1, 13)]         # fallback tiếng Anh
keyword_pcc = "PCC"
keyword_space = "Space(centimeter)"

# =======================
# HELPER FUNCTIONS
# =======================
def detect_encoding(path, sample_size=50000):
    with open(path, "rb") as f:
        raw = f.read(sample_size)
    detected = chardet.detect(raw)
    return detected.get("encoding") or "utf-8"

def smart_read_csv_lines(path):
    """Đọc file CSV “linh hoạt”: tự detect encoding + split thủ công."""
    encoding = detect_encoding(path)
    lines_parsed = []

    with open(path, "r", encoding=encoding, errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            split_line = [s.strip() for s in re.split(r"[\t,;|]", line) if s.strip()]
            if split_line:
                lines_parsed.append(split_line)
    return lines_parsed

def find_first_containing(lines, key):
    """Tìm ô đầu tiên CHỨA key (không cần giống hệt, case-insensitive)."""
    key_lower = key.lower()
    for i, row in enumerate(lines):
        for j, cell in enumerate(row):
            if key_lower in cell.lower():
                return i, j
    return None

def find_first_containing_regex(lines, pattern):
    """Tìm ô đầu tiên match regex (case-insensitive)."""
    regex = re.compile(pattern, re.IGNORECASE)
    for i, row in enumerate(lines):
        for j, cell in enumerate(row):
            if regex.search(cell):
                return i, j
    return None

def get_neighbor_value(lines, i, j):
    """Lấy ô bên phải ưu tiên, nếu trống lấy ô dưới, nếu vẫn trống lấy inline."""
    nrows = len(lines)
    ncols = len(lines[i])

    # right
    if j + 1 < ncols and lines[i][j + 1].strip():
        return lines[i][j + 1].strip()

    # below
    if i + 1 < nrows and j < len(lines[i + 1]) and lines[i + 1][j].strip():
        return lines[i + 1][j].strip()

    # inline sau dấu ':' hoặc khoảng trắng
    cell = lines[i][j]
    for sep in [":", "：", "\t", " "]:
        if sep in cell:
            parts = cell.split(sep, 1)
            if len(parts) > 1 and parts[1].strip():
                return parts[1].strip()
    return ""

def get_zone_value(lines, i, j):
    """Lấy giá trị zone, ưu tiên ô dưới, nếu trống ô bên phải, nếu trống thì inline."""
    nrows = len(lines)
    ncols = len(lines[i])

    # below
    if i + 1 < nrows and j < len(lines[i + 1]) and lines[i + 1][j].strip():
        return lines[i + 1][j].strip()

    # right
    if j + 1 < ncols and lines[i][j + 1].strip():
        return lines[i][j + 1].strip()

    # inline: tìm số trong cell
    cell = lines[i][j]
    m = re.findall(r"[\d.]+", cell)
    if m:
        return m[0]
    return ""

def get_space_value(lines, i, j):
    """Lấy ô thứ 2 bên dưới."""
    if i + 2 < len(lines) and j < len(lines[i + 2]):
        return lines[i + 2][j].strip()
    return ""

# =======================
# MAIN PROCESS
# =======================
records = []

csv_files = sorted(glob.glob(os.path.join(source_dir, "*.csv")))
if not csv_files:
    print("⚠️ Không tìm thấy file CSV trong thư mục:", source_dir)

for csv_path in csv_files:
    try:
        lines = smart_read_csv_lines(csv_path)
    except Exception as e:
        print(f"⚠️ Lỗi đọc file {csv_path}: {e}")
        continue

    result = {"File Name": os.path.basename(csv_path)}

    # (1) Product/Processing/Stove
    for key in keywords_first:
        pos = find_first_containing(lines, key)
        result[key] = get_neighbor_value(lines, *pos) if pos else ""

    # (2) Zones 1–12
    for i in range(1, 13):
        # CN zone với khoảng trắng tùy ý
        key_cn_pattern = f"温区\\s*{i}"
        pos = find_first_containing_regex(lines, key_cn_pattern)
        if pos:
            val = get_zone_value(lines, *pos)
        else:
            # fallback tiếng Anh
            key_en = f"Area {i}"
            pos = find_first_containing(lines, key_en)
            val = get_zone_value(lines, *pos) if pos else ""
        result[f"zone {i}"] = val

    # (3) PCC
    pos = find_first_containing(lines, keyword_pcc)
    result[keyword_pcc] = get_neighbor_value(lines, *pos) if pos else ""

    # (4) Space
    pos = find_first_containing(lines, keyword_space)
    result[keyword_space] = get_space_value(lines, *pos) if pos else ""

    records.append(result)
    print(f"✅ Processed: {os.path.basename(csv_path)}")

# --- Xuất CSV tổng hợp ---
if records:
    out_df = pd.DataFrame(records)
    cols_order = ["File Name"] + keywords_first + [f"zone {i}" for i in range(1,13)] + [keyword_pcc, keyword_space]
    for c in cols_order:
        if c not in out_df.columns:
            out_df[c] = ""
    out_df = out_df[cols_order]
    out_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"🎯 Hoàn tất! Kết quả lưu tại: {output_file}")
else:
    print("⚠️ Không có bản ghi hợp lệ để xuất.")
