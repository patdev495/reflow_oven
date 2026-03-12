from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import joblib
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
import threading
import webbrowser
import time

# ===============================
# 1️⃣ Load mô hình & scaler
# ===============================
model = joblib.load(r"models\xgb_model.pkl")
x_scaler = joblib.load(r"models\xgb_x_scaler.pkl")
y_scaler = joblib.load(r"models\xgb_y_scaler.pkl")

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
    allow_origins=["*"],       
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# 3️⃣ Serve giao diện index.html
# ===============================
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_index():
    return FileResponse("static/index.html")


# ===============================
# 4️⃣ Schema input/output
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
# 5️⃣ Hàm dự đoán
# ===============================
def predict_temperature_profile(inputs: list[float], speed: float):
    features = np.array(inputs + [speed], dtype=float).reshape(1, -1)

    zones = np.arange(1, n_zones + 1).reshape(-1, 1)
    zone_scaled = zones / n_zones
    X_rep = np.repeat(features, n_zones, axis=0)
    X_new = np.hstack([X_rep, zone_scaled])

    X_scaled = x_scaler.transform(X_new)
    y_pred_scaled = model.predict(X_scaled)
    y_pred = y_scaler.inverse_transform(y_pred_scaled.reshape(-1, 1)).ravel()
    return y_pred.tolist()


# ===============================
# 6️⃣ API Endpoint
# ===============================
@app.post("/reflow_predict", response_model=TemperatureResponse)
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
    
    time.sleep(1)
    y_pred = predict_temperature_profile(inputs, data.speed)
    return {"predicted_temperatures": y_pred}


# ===============================
# 7️⃣ Auto mở trình duyệt khi chạy
# ===============================
def open_browser():
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:8002")


# ===============================
# 8️⃣ Run server
# ===============================
if __name__ == "__main__":
    import uvicorn
    threading.Thread(target=open_browser).start()
    uvicorn.run(app, host="0.0.0.0", port=8002)
