from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
import time
from global_params import main_params
# ===============================
# 1️⃣ Load mô hình & scaler
# ===============================
model_dir = main_params.model_dir
model = joblib.load(rf"{model_dir}\xgb_model.pkl")
x_scaler = joblib.load(rf"{model_dir}\xgb_x_scaler.pkl")
y_scaler = joblib.load(rf"{model_dir}\xgb_y_scaler.pkl")

n_zones = 10  # số zone giống khi train

# ===============================
# 2️⃣ Định nghĩa API app
# ===============================
app = FastAPI(
    title="Temperature Profile Prediction API",
    description="Predicts 10-zone temperature profile based on product specs and line speed.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Cho phép tất cả domain
    allow_credentials=True,
    allow_methods=["*"],        # Cho phép mọi phương thức (GET, POST, PUT, DELETE, OPTIONS,...)
    allow_headers=["*"],        # Cho phép tất cả header (Authorization, Content-Type,...)
)
# ===============================
# 3️⃣ Schema input/output
# ===============================
class ProductInput(BaseModel):
    bot: float
    top: float
    panel: float
    length: float
    width: float
    height: float
    fixture: float
    iron_frame: float
    speed: float


class TemperatureResponse(BaseModel):
    predicted_temperatures: list[float]


# ===============================
# 4️⃣ Hàm dự đoán
# ===============================
def predict_temperature_profile(inputs: list[float], speed: float):
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
    return y_pred.tolist()


# ===============================
# 5️⃣ API Endpoint
# ===============================
@app.post(main_params.endpoint_url, response_model=TemperatureResponse)
def predict_temperature(data: ProductInput):
    """
    Nhận vào thông số sản phẩm và tốc độ, trả ra 10 vùng nhiệt độ dự đoán.
    """
    inputs = [
        data.bot,
        data.top,
        data.panel,
        data.length,
        data.width,
        data.height,
        data.fixture,
        data.iron_frame,
    ]
    
    time.sleep(main_params.prediction_delay)
    y_pred = predict_temperature_profile(inputs, data.speed)
    return {main_params.response_key: y_pred}


# ===============================
# 6️⃣ Run server (dev)
# ===============================
# Chạy bằng lệnh: uvicorn app:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=main_params.api_port)
