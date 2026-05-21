# Reflow Oven Temperature Prediction System 🔥📊

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com/)
[![XGBoost](https://img.shields.io/badge/XGBoost-Regressor-green?style=for-the-badge)](https://xgboost.readthedocs.io/)
[![Chart.js](https://img.shields.io/badge/Chart.js-F5788D?style=for-the-badge&logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyInstaller](https://img.shields.io/badge/PyInstaller-Executable-blue?style=for-the-badge)](https://pyinstaller.org/)

**Reflow Oven Temperature Prediction System** là hệ thống phân tích và dự đoán phân bố nhiệt độ 10 vùng (10-Zone Temperature Profile) của lò hàn Reflow trong dây chuyền sản xuất và lắp ráp linh kiện điện tử trên bản mạch in (**SMT - Surface Mount Technology**). 

Hệ thống sử dụng thuật toán học máy mạnh mẽ **XGBoost Regressor** kết hợp với phương pháp cấu trúc dữ liệu dạng dọc (**Long-Format Architecture**) để dự đoán chính xác đường cong nhiệt độ tối ưu dựa trên thông số hình học của PCB, jig/đồ gá và tốc độ xích tải của lò hàn.

---

## 📖 Thuật ngữ Nghiệp vụ (Domain Language)

Để đảm bảo tính nhất quán trong vận hành và kỹ thuật SMT, dự án sử dụng các thuật ngữ tiêu chuẩn sau:

*   **Reflow Oven (Lò hàn Reflow)**: Lò gia nhiệt nhiều vùng nhiệt độ nối tiếp nhau nhằm làm nóng chảy kem hàn (solder paste), hoàn tất liên kết cơ-điện giữa linh kiện và mạch in PCB.
*   **Heating Zones (Các vùng gia nhiệt)**: Các vùng kiểm soát nhiệt độc lập trong lò. Hệ thống này mô hình hóa lò hàn gồm **10 vùng nhiệt độ** nối tiếp nhau (Zone 1 - Zone 10).
*   **Temperature Profile (Profile nhiệt độ)**: Đường cong biểu diễn sự biến thiên nhiệt độ của bo mạch PCB khi đi qua 10 vùng gia nhiệt của lò reflow.
*   **Product Specifications (Thông số sản phẩm & PCB)**:
    *   **BOT / TOP (Số lượng linh kiện mặt dưới / mặt trên)**: Mật độ hoặc số lượng linh kiện dán trên hai mặt của bảng mạch PCB.
    *   **Panel (Mạch ghép)**: Số lượng bo mạch con được ghép chung trên một bảng lớn (panel).
    *   **Length / Width / Height (Dài / Rộng / Cao)**: Kích thước hình học vật lý của tấm PCB (đơn vị: mm).
    *   **Fixture (Jig/Đồ gá)**: Khung đỡ kim loại giữ PCB phẳng khi đi qua lò nhiệt cao (`1`: sử dụng đồ gá, `0`: không sử dụng).
    *   **Iron Frame (Khung sắt bảo vệ)**: Khung viền gia cố PCB chống cong vênh do sốc nhiệt (`1`: sử dụng khung, `0`: không sử dụng).
    *   **Speed (Tốc độ xích tải)**: Tốc độ băng truyền kéo bo mạch qua lò (đơn vị: cm/phút).
*   **Actual Profile (Profile thực tế)**: Dữ liệu nhiệt độ đo đạc thực tế của PCB bằng thiết bị đo chuyên dụng (như máy đo nhiệt KIC hoặc Datapaq), dùng để kiểm chứng và phân tích sai lệch.
*   **Deviation (Độ lệch nhiệt độ)**: Mức chênh lệch nhiệt độ giữa Profile dự đoán từ học máy và Profile đo đạc thực tế tại từng vùng gia nhiệt.

---

## 🧠 Kiến trúc Mô hình Học máy (Machine Learning Architecture)

Điểm cốt lõi tạo nên sự đột phá về hiệu năng và độ chính xác của dự án nằm ở **Kiến trúc dữ liệu dạng dọc (Long-Format)**:

```text
CÁCH TIẾP CẬN THÔNG THƯỜNG (Dễ sai số):
[PCB Specs + Speed] ──> [10 Mô hình XGBoost độc lập] ──> [10 Nhiệt độ Zone]

CÁCH TIẾP CẬN MỚI (Tối ưu hóa liên tục):
[PCB Specs + Speed] ──┐
                      ├─> [1 Mô hình XGBoost Duy Nhất] ──> [Nhiệt độ cụ thể của Zone đó]
[Zone Index (0.1-1.0)] ┘
```

*   **Một Mô hình Duy Nhất**: Thay vì xây dựng 10 mô hình học máy khác nhau cho 10 vùng (gây nặng tải và mất tính liên kết), hệ thống mở rộng dữ liệu thành cấu trúc dọc (Long-Format).
*   **Tham số Hóa Vùng (Zone Index Parameterization)**: Chỉ số vùng (từ 1 đến 10) được chuẩn hóa tuyến tính về khoảng `[0.1, 1.0]` và đưa trực tiếp vào làm một thuộc tính đầu vào (Feature) cùng với các thông số PCB.
*   **Tính Liên tục**: Mô hình XGBoost học được mối quan hệ vật lý phi tuyến tính trơn tru giữa vị trí bo mạch trong lò và sự gia nhiệt, từ đó đạt sai số tuyệt đối trung bình (**MAE**) cực kỳ thấp trên toàn bộ các zone.

---

## 🏗️ Kiến trúc Hệ thống

Dự án được cấu trúc gọn nhẹ, hỗ trợ triển khai linh hoạt (Self-hosted chạy local hoặc Cloud Web Service):

```mermaid
graph LR
    subgraph Frontend (HTML5 / JS Client)
        UI[index.html - Giao diện Nhập liệu & Đồ thị]
        Chart[Chart.js - Trực quan hóa Đường cong Nhiệt]
    end

    subgraph Backend API (FastAPI Server)
        API[main_api_selfhost.py]
        Engine[Predict Engine]
        Model[(XGBoost Model: xgb_model.pkl)]
    end

    UI -->|POST: /reflow_predict| API
    API --> Engine
    Engine -->|Inference| Model
    Model -->|10-Zone Temps| UI
    Chart -->|So sánh trực quan| UI
```

1.  **Backend (FastAPI)**: 
    *   Sử dụng tệp `main_api.py` hoặc `main_api_selfhost.py` để cấu hình API RESTful tiếp nhận tham số PCB.
    *   Tự động tải mô hình đã được đóng băng (`xgb_model.pkl`) cùng bộ scaler chuẩn hóa đầu vào/đầu ra (`xgb_x_scaler.pkl`, `xgb_y_scaler.pkl`) từ thư mục `models`.
2.  **Frontend (Web UI & Chart.js)**:
    *   Giao diện người dùng đơn trang (Single-Page App) trực quan cao với CSS HSL hiện đại.
    *   Hỗ trợ nhập thông số sản phẩm và **nhập tùy chọn Profile thực tế** để thực hiện phân tích đối chiếu.
    *   Tự động tính toán độ lệch nhiệt độ cụ thể trên từng Zone, kèm phân loại cảnh báo màu sắc (Xanh lá: Khớp tốt, Vàng: Cảnh báo nhẹ, Đỏ: Lệch quá mức cho phép).
3.  **Self-Host desktop-mode**:
    *   Tệp `main_api_selfhost.py` cho phép khởi chạy server và tự động kích hoạt trình duyệt web mở giao diện ứng dụng tại địa chỉ `http://127.0.0.1:8002`.

---

## 📂 Cấu trúc Thư mục Dự án

```text
reflow_oven/
├── models/
│   └── model_old/              # Chứa các file mô hình học máy và scaler đã train
│       ├── xgb_model.pkl       # Mô hình XGBoost Regressor đã đóng băng
│       ├── xgb_x_scaler.pkl    # StandardScaler cho các thuộc tính đầu vào
│       └── xgb_y_scaler.pkl    # StandardScaler cho nhiệt độ đầu ra
├── static/
│   └── index.html              # Giao diện Web UI (được phục vụ bởi selfhost API)
├── util/                       # Thư mục chứa các script hỗ trợ lọc và xử lý dữ liệu
│   ├── summary.py              # Script tổng hợp và phân tích dữ liệu lò reflow
│   ├── get_product.py          # Lọc dữ liệu thông số sản phẩm PCB
│   └── final.py                # Xử lý bước cuối cho dữ liệu huấn luyện
├── Reflow_Machine_Docs/        # Thư mục lưu tài liệu chuyên ngành lò hàn SMT (PDF & PPT)
├── global_params.py            # Khởi tạo tham số hệ thống từ class BaseParams
├── reflow_config.yaml          # File cấu hình YAML lưu cổng API và đường dẫn model
├── main_XGBoot_10_zones.py     # Script huấn luyện mô hình XGBoost chính + Phân tích SHAP/Feature Importance
├── predict_XGboot.py           # Script chạy dự đoán thử nghiệm offline
├── main_api.py                 # API FastAPI chính (chạy độc lập)
├── main_api_selfhost.py        # API FastAPI tự phục vụ giao diện và tự động mở trình duyệt
├── index.html                  # Bản sao giao diện UI tại thư mục gốc
└── README.md                   # Hướng dẫn chi tiết hệ thống (Tiếng Việt)
```

---

## 🚀 Hướng dẫn Cài đặt & Vận hành

### 📋 Yêu cầu Cài đặt
Đảm bảo máy trạm đã cài đặt **Python 3.10** trở lên và công cụ quản lý thư viện **uv** để khởi chạy siêu tốc.

---

### 💻 Khởi chạy Ứng dụng Cục bộ (Self-hosted Web)

Để khởi động đồng thời cả API Server và mở giao diện Web phân tích nhiệt độ tự động:
```powershell
uv run python main_api_selfhost.py
```
Hệ thống sẽ:
1.  Bật dịch vụ FastAPI tại cổng `8002`.
2.  Tự động nạp mô hình XGBoost từ đường dẫn `models/model_old`.
3.  Kích hoạt trình duyệt mặc định truy cập `http://127.0.0.1:8002` hiển thị giao diện phân tích.

---

### 🧠 Huấn luyện lại Mô hình Học máy (Re-train Model)

Nếu bạn có dữ liệu mới đo đạc từ nhà xưởng và muốn cập nhật mô hình:

1.  Chuẩn bị tệp dữ liệu đã dọn dẹp đặt tên là `summary.csv` trong thư mục gốc. Tệp cần chứa các cột thông số vật lý (`x1` đến `x8`), tốc độ `Speed` và 10 cột nhiệt độ thực tế (`zone 1` đến `zone 10`).
2.  Chạy script huấn luyện chính:
    ```powershell
    uv run python main_XGBoot_10_zones.py
    ```
3.  Quy trình chạy tự động bao gồm:
    *   **Data Cleaning & Preprocessing**: Tự động lọc giá trị NaN và ép kiểu số.
    *   **Long-Format expansion**: Tự động tái cấu trúc bảng dữ liệu sang định dạng dọc, chuẩn hóa chỉ số vùng.
    *   **Normalization**: Tính toán lại `StandardScaler` cho cả đầu vào và mục tiêu.
    *   **XGBoost Training**: Huấn luyện với tham số tối ưu (600 cây, học suất 0.05, hàm lỗi Pseudo-Huber chống nhiễu sốc nhiệt).
    *   **Evaluation**: Tính toán và hiển thị sai số tuyệt đối trung bình (**MAE**).
    *   **Interpretability**: Tự động hiển thị biểu đồ độ quan trọng thuộc tính (**Feature Importance - Gain**) và thực hiện phân tích lực tác động sinh học **SHAP (Waterall & Summary plot)** để giải thích trực quan quyết định của AI.
    *   **Model Freezing**: Ghi đè các tệp `.pkl` mới vào thư mục.

---

### 📦 Đóng gói Thành phẩm độc lập (.EXE)

Để biên dịch API Backend thành file thực thi độc lập không phụ thuộc môi trường Python:
```powershell
pyinstaller --noconfirm --clean main_api.py
```
File thực thi sau khi hoàn thành sẽ nằm trong thư mục `dist/main_api`.

---

## 🛠️ Cấu hình Tùy chỉnh (`reflow_config.yaml`)

Bạn có thể thay đổi cấu hình cổng dịch vụ và đường dẫn tải mô hình trực tiếp trong tệp cấu hình mà không cần sửa code:
```yaml
main:
  endpoint_url: /reflow_predict
  response_key: predicted_temperatures
  api_port: 4446                 # Cổng kết nối của giao diện UI mặc định
  prediction_delay: 1            # Giả lập thời gian xử lý của AI (giây)
  model_dir: models\model_old    # Thư mục tải mô hình hoạt động
```
