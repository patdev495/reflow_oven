import pandas as pd
import os

def match_products_to_files(products_file, filelist_file, output_file):
    # Đọc dữ liệu từ 2 file Excel
    df_products = pd.read_excel(products_file, dtype=str)
    df_files = pd.read_csv(filelist_file, dtype=str)

    # Chuẩn hóa dữ liệu
    df_products['products'] = df_products['products'].fillna('').str.strip()
    df_files['File Name'] = df_files['File Name'].fillna('').str.strip()

    results = []

    # Duyệt từng product
    for product in df_products['products']:
        if not product:
            continue  # bỏ qua ô trống

        # Tìm kiếm: không phân biệt hoa/thường, không dùng regex
        matches = df_files[df_files['File Name'].str.contains(product, case=False, na=False, regex=False)]

        if not matches.empty:
            first_row = True
            for _, row in matches.iterrows():
                record = row.to_dict()
                record["Product"] = product if first_row else ""  # chỉ ghi product ở dòng đầu
                results.append(record)
                first_row = False
        else:
            # Nếu không tìm thấy file nào, vẫn ghi product (để biết product đó không match)
            results.append({"Product": product, "File Name": "❌ Không tìm thấy", **{col: "" for col in df_files.columns if col != "File Name"}})

    # Tạo DataFrame kết quả
    df_out = pd.DataFrame(results)

    # Đưa cột Product lên đầu
    cols = ["Product"] + [c for c in df_out.columns if c != "Product"]
    df_out = df_out[cols]

    # Ghi kết quả ra file Excel
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df_out.to_excel(output_file, index=False, engine='openpyxl')

    print(f"✅ Đã lưu {len(df_out)} dòng kết quả vào: {output_file}")


if __name__ == "__main__":
    products_file = r"F:\dev\reflow\PCBs.xlsx"
    filelist_file = r"F:\dev\reflow\file_list.csv"
    output_file = r"F:\dev\reflow\matched_results.xlsx"

    match_products_to_files(products_file, filelist_file, output_file)
