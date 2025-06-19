import os
import pandas as pd

def read_csv_with_fallback(path):
    """Thử đọc file CSV với nhiều encoding khác nhau."""
    encodings_to_try = ['utf-8-sig', 'utf-16', 'utf-8', 'cp932', 'gbk', 'latin1']
    for enc in encodings_to_try:
        try:
            return pd.read_csv(path, header=None, dtype=str, encoding=enc)
        except Exception:
            continue
    raise ValueError("Không đọc được file CSV với các encoding thông thường.")

def extract_first_product_name(src_dir, output_file):
    results = []

    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.lower().endswith(('.csv', '.xlsx')):
                file_path = os.path.join(root, file)
                print(f"🔍 Đang xử lý: {file_path}")

                try:
                    # Đọc dữ liệu
                    if file.lower().endswith('.csv'):
                        df = read_csv_with_fallback(file_path)
                    else:
                        df = pd.read_excel(file_path, header=None, dtype=str)

                    found = False

                    # Duyệt ô từ trên xuống
                    for i in range(df.shape[0]):
                        for j in range(df.shape[1]):
                            val = str(df.iat[i, j]).strip().lower()
                            if "product name" in val:
                                if j + 1 < df.shape[1]:
                                    product_value = str(df.iat[i, j + 1]).strip()
                                else:
                                    product_value = ""
                                results.append({
                                    "File": file,
                                    "Product Name": product_value
                                })
                                print(f"✅ {file}: {product_value}")
                                found = True
                                break
                        if found:
                            break

                except Exception as e:
                    print(f"⚠️ Lỗi đọc {file_path}: {e}")

    if results:
        df_out = pd.DataFrame(results)
        df_out.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 Đã lưu {len(results)} dòng vào: {output_file}")
    else:
        print("\n❌ Không tìm thấy 'Product Name' trong bất kỳ file nào.")

if __name__ == "__main__":
    src_folder = r"DuLieu_CSV_XLSX"          # Thư mục chứa file nguồn
    output_file = r"products.csv"       # File kết quả

    extract_first_product_name(src_folder, output_file)
