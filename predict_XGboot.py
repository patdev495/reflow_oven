import joblib
import numpy as np
import matplotlib.pyplot as plt
from global_params import main_params
# ===============================
# 1️⃣ Load mô hình và scaler
# ===============================
model_dir = main_params.model_dir
model = joblib.load(rf"{model_dir}\xgb_model.pkl")
x_scaler = joblib.load(rf"{model_dir}\xgb_x_scaler.pkl")
y_scaler = joblib.load(rf"{model_dir}\xgb_y_scaler.pkl")

n_zones = 10  # số zone giống khi train


# ===============================
# 2️⃣ Hàm dự đoán profile nhiệt độ
# ===============================
def predict_temperature_profile(inputs, speed):
    """
    inputs: list[float] gồm 8 thông số sản phẩm
    speed: float - tốc độ line
    return: numpy.ndarray gồm 10 giá trị nhiệt độ dự đoán
    """
    features = np.array(inputs + [speed], dtype=float).reshape(1, -1)

    # Tạo dữ liệu cho 10 zone
    zones = np.arange(1, n_zones + 1).reshape(-1, 1)
    zone_scaled = zones / n_zones
    X_rep = np.repeat(features, n_zones, axis=0)
    X_new = np.hstack([X_rep, zone_scaled])

    # Chuẩn hóa & dự đoán
    X_scaled = x_scaler.transform(X_new)
    y_pred_scaled = model.predict(X_scaled)
    y_pred = y_scaler.inverse_transform(y_pred_scaled.reshape(-1, 1)).ravel()
    return y_pred

# ===============================
# 3️⃣ Hàm vẽ & so sánh kết quả
# ===============================
def plot_predicted_vs_actual(y_pred, y_actual, save_path="predicted_vs_actual.png"):
    """
    Vẽ biểu đồ và in so sánh giữa profile dự đoán và thực tế.
    """
    abs_diff = np.abs(y_pred - y_actual)

    print("\n=== 🔥 Profile Predicted vs Actual ===")
    for i, (pred, real, diff) in enumerate(zip(y_pred, y_actual, abs_diff), start=1):
        print(f"Zone {i:2d}: Pred = {pred:.2f} °C | Actual = {real:.2f} °C | Δ = {diff:.2f} °C")

    mean_deviation = abs_diff.mean()
    print(f"\n📊 Độ lệch trung bình giữa dự đoán và thực tế: {mean_deviation:.2f} °C")

    # Vẽ biểu đồ
    plt.figure(figsize=(8, 4))
    plt.plot(range(1, n_zones + 1), y_pred, 'o--', label='Predicted')
    plt.plot(range(1, n_zones + 1), y_actual, 's-', label='Actual')
    plt.xlabel("Zone index")
    plt.ylabel("Temperature (°C)")
    plt.title("Predicted vs Actual Profile")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xticks(range(1, n_zones + 1))
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.show()

    print(f"✅ Saved plot to: {save_path}\n")


# ===============================
# 4️⃣ Vòng lặp nhập liệu nhiều sản phẩm
# ===============================
params = ["BOT", "TOP", "panel", "length", "width", "height", "fixture?", "iron frame?"]

print("=== 🔁 Model ready — nhập nhiều bộ dữ liệu, gõ 'q' để thoát ===\n")

while True:
    print("\n=== Input new product spec ===")
    cmd = input("Nhập 'q' để thoát hoặc Enter để tiếp tục: ").strip().lower()
    if cmd in ["q", "exit"]:
        print("👋 Kết thúc chương trình.")
        break

    # Thu thập thông tin sản phẩm
    inputs = []
    for p in params:
        while True:
            try:
                val = float(input(f"{p}: "))
                inputs.append(val)
                break
            except ValueError:
                print("❌ Vui lòng nhập số hợp lệ.")

    # Nhập tốc độ
    while True:
        try:
            speed = float(input("Speed: "))
            break
        except ValueError:
            print("❌ Vui lòng nhập số hợp lệ.")

    # Gọi hàm dự đoán
    y_pred = predict_temperature_profile(inputs, speed)

    print("\n=== 🔥 Profile Dự Đoán ===")
    for i, temp in enumerate(y_pred, start=1):
        print(f"Zone {i:2d}: {temp:.2f} °C")

    # Nhập profile thực tế nếu có
    choice = input("\nNhập profile thực tế để so sánh? (y/n): ").strip().lower()
    if choice != "y":
        print("✅ Bỏ qua phần so sánh.\n")
        continue

    print("\n=== 📏 Nhập profile thực tế (10 giá trị, cách nhau bằng dấu cách) ===")
    while True:
        try:
            y_actual = list(map(float, input("Nhập 10 giá trị °C: ").split()))
            if len(y_actual) != n_zones:
                print(f"⚠️ Cần nhập đúng {n_zones} giá trị.")
                continue
            y_actual = np.array(y_actual)
            break
        except ValueError:
            print("❌ Vui lòng nhập các số hợp lệ, cách nhau bằng dấu cách.")

    # Gọi hàm vẽ & so sánh
    plot_predicted_vs_actual(y_pred, y_actual)
