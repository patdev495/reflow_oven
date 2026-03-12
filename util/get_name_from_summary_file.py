import pandas as pd

# Đọc file CSV
df = pd.read_csv("summary11.csv")

# 1. Xử lý cột Product Name
df["Product Name"] = df["Product Name"].str.replace(
    r"-\d+R1A.*$", "", regex=True
)

# 2. Xử lý cột PCC: lấy số % (bỏ chữ Good, bỏ .00, bỏ %)
df["PCC"] = (
    df["PCC"]
    .str.extract(r"(\d+)(?:\.\d+)?%")  # lấy phần số trước dấu %
)

# (tuỳ chọn) chuyển PCC sang kiểu số
df["PCC"] = df["PCC"].astype("Int64")

# Lưu ra file mới
df.to_csv("summary11_cut.csv", index=False, encoding="utf-8-sig")
