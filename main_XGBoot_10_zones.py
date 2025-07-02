# ==========================================
# 🔥 Reflow Temperature Prediction – XGBoost Modular
# ==========================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor, plot_importance
import shap

# ==========================================
# 1️⃣ ĐỌC VÀ TIỀN XỬ LÍ DỮ LIỆU
# ==========================================
def load_and_clean_data(filepath):
    df = pd.read_csv(filepath)

    # Bỏ cột không dùng
    if "SN" in df.columns:
        df = df.drop(columns=["SN"])

    print(f"✅ Số dòng dữ liệu: {len(df)}")
    print(f"✅ Các cột: {df.columns.tolist()}")

    # Ép kiểu số
    df = df.apply(pd.to_numeric, errors='coerce')

    # Bỏ NaN
    print("🔍 Kiểm tra NaN:")
    print(df.isna().sum())
    df = df.dropna()
    print(f"✅ Sau khi bỏ NaN: còn {len(df)} dòng hợp lệ.")

    return df


def prepare_long_format(df, feature_cols, zone_cols):
    X_raw = df[feature_cols].values
    Y_raw = df[zone_cols].values
    n_samples, n_zones = Y_raw.shape

    # Mở rộng long format: mỗi hàng = 1 zone
    zone_idx = np.tile(np.arange(1, n_zones + 1), n_samples).reshape(-1, 1)
    zone_scaled = zone_idx / n_zones
    X_long = np.repeat(X_raw, n_zones, axis=0)
    X_long = np.hstack([X_long, zone_scaled])
    Y_long = Y_raw.reshape(-1, 1)

    print(f"📊 Dữ liệu long-format: X={X_long.shape}, Y={Y_long.shape}")
    return X_long, Y_long


# ==========================================
# 2️⃣ CHUẨN HÓA FEATURE
# ==========================================
def scale_features(X, Y):
    x_scaler = StandardScaler()
    y_scaler = StandardScaler()
    X_scaled = x_scaler.fit_transform(X)
    Y_scaled = y_scaler.fit_transform(Y).ravel()
    return X_scaled, Y_scaled, x_scaler, y_scaler


# ==========================================
# 3️⃣ TRAIN XGBOOST
# ==========================================
def train_xgb(X_train, Y_train, **kwargs):
    model = XGBRegressor(
        n_estimators=600,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.9,
        colsample_bytree=0.9,
        objective='reg:pseudohubererror',
        random_state=42,
        tree_method='hist',
        **kwargs
    )
    print("🚀 Đang huấn luyện mô hình XGBoost ...")
    model.fit(X_train, Y_train)
    print("✅ Huấn luyện xong!")
    return model


# ==========================================
# 4️⃣ ĐÁNH GIÁ MÔ HÌNH
# ==========================================
def evaluate_model(model, X_test, Y_test, y_scaler):
    Y_pred_scaled = model.predict(X_test)
    Y_pred = y_scaler.inverse_transform(Y_pred_scaled.reshape(-1, 1)).ravel()
    Y_true = y_scaler.inverse_transform(Y_test.reshape(-1, 1)).ravel()
    mae = mean_absolute_error(Y_true, Y_pred)
    print(f"🎯 MAE trung bình: {mae:.3f} °C")
    return Y_true, Y_pred


# ==========================================
# 5️⃣ PHÂN TÍCH FEATURE IMPORTANCE
# ==========================================
def plot_feature_importance(model, feature_names):
    importance = model.feature_importances_
    fi_df = pd.DataFrame({
        "Feature": feature_names,
        "Importance": importance
    }).sort_values("Importance", ascending=False)
    print("\n📊 Feature importance (từ model):")
    print(fi_df)

    plt.figure(figsize=(8,4))
    plt.barh(fi_df["Feature"], fi_df["Importance"], color="skyblue")
    plt.gca().invert_yaxis()
    plt.title("🔍 Feature Importance – XGBoost")
    plt.xlabel("Độ quan trọng")
    plt.tight_layout()
    plt.show()

    plot_importance(model, importance_type="gain", xlabel="Gain", height=0.5)
    plt.title("Feature Importance (Gain)")
    plt.tight_layout()
    plt.show()


def shap_analysis(model, X_train, X_test, feature_names):
    print("\n💡 Đang tính toán giá trị SHAP (mất vài giây)...")
    explainer = shap.Explainer(model, X_train, feature_names=feature_names)
    shap_values = explainer(X_test)
    shap.summary_plot(shap_values, features=X_test, feature_names=feature_names)
    shap.plots.waterfall(shap_values[0])


# ==========================================
# 6️⃣ DỰ ĐOÁN PROFILE MỚI
# ==========================================
def predict_profile(model, x_phys, n_zones, x_scaler, y_scaler):
    zones = np.arange(1, n_zones + 1).reshape(-1, 1)
    zones_scaled = zones / n_zones
    X_pred = np.hstack([np.repeat(x_phys, len(zones), axis=0), zones_scaled])
    Y_pred_scaled = model.predict(x_scaler.transform(X_pred))
    Y_pred = y_scaler.inverse_transform(Y_pred_scaled.reshape(-1,1)).ravel()
    return Y_pred


# ==========================================
# 7️⃣ VẼ PROFILE SO SÁNH
# ==========================================
def plot_profile(Y_true_profile, Y_pred_profile):
    plt.figure(figsize=(7,4))
    plt.plot(range(1, len(Y_true_profile)+1), Y_true_profile, 'o-', label='Thực tế', linewidth=2)
    plt.plot(range(1, len(Y_pred_profile)+1), Y_pred_profile, 's--', label='Dự đoán XGBoost', linewidth=2)
    plt.xlabel("Zone index")
    plt.ylabel("Temperature (°C)")
    plt.title("So sánh Profile nhiệt độ (Thực tế vs Dự đoán – XGBoost)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# ==========================================
# 8️⃣ MAIN
# ==========================================
def main():
    # ---- Load & clean
    df = load_and_clean_data("summary.csv")
    feature_cols = ["x1","x2","x3","x4","x5","x6","x7","x8","Speed"]
    zone_cols = [f"zone {i}" for i in range(1, 11)]

    # ---- Prepare long format
    X_long, Y_long = prepare_long_format(df, feature_cols, zone_cols)

    # ---- Scale
    X_scaled, Y_scaled, x_scaler, y_scaler = scale_features(X_long, Y_long)

    # ---- Train/test split
    X_train, X_test, Y_train, Y_test = train_test_split(
        X_scaled, Y_scaled, test_size=0.1, random_state=42
    )

    # ---- Train model
    model = train_xgb(X_train, Y_train)

    # ---- Save model & scaler
    joblib.dump(model, "xgb_model.pkl")
    joblib.dump(x_scaler, "xgb_x_scaler.pkl")
    joblib.dump(y_scaler, "xgb_y_scaler.pkl")

    # ---- Evaluate
    Y_true, Y_pred = evaluate_model(model, X_test, Y_test, y_scaler)

    # ---- Feature importance
    feature_names = feature_cols + ["zone_index"]
    plot_feature_importance(model, feature_names)
    shap_analysis(model, X_train, X_test, feature_names)

    # ---- Predict & plot sample profile
    sample_i = 0
    x_phys = df[feature_cols].values[sample_i].reshape(1,-1)
    Y_pred_profile = predict_profile(model, x_phys, n_zones=len(zone_cols), x_scaler=x_scaler, y_scaler=y_scaler)
    Y_true_profile = df[zone_cols].values[sample_i]
    plot_profile(Y_true_profile, Y_pred_profile)

    print("✅ Hoàn tất toàn bộ quy trình.")


if __name__ == "__main__":
    main()

