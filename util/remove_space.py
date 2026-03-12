import pandas as pd

input_file = r"products_trim.csv"
output_file = r"products_trim_1.csv"

# Đọc file
df = pd.read_csv(input_file, dtype=str)

# Loại bỏ phần sau dấu cách cuối cùng
df = df.applymap(lambda x: str(x).rsplit(' ', 1)[0] if isinstance(x, str) and ' ' in x else x)

# Ghi lại file mới
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"✅ Đã lưu file đã xử lý: {output_file}")
