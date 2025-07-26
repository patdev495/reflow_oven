# ==========================================
# 🔥 Reflow Temperature Prediction – XGBoost (with U)
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
# 1️⃣ LOAD & CLEAN DATA
# ==========================================
def load_and_clean_data(filepath):
    df = pd.read_csv(filepath)

    # Drop unused column
    if "SN" in df.columns:
        df = df.drop(columns=["SN"])

    print(f"✅ Total samples: {len(df)}")
    print(f"✅ Columns: {df.columns.tolist()}")

    # Force numeric
    df = df.apply(pd.to_numeric, errors="coerce")

    print("🔍 NaN check:")
    print(df.isna().sum())

    df = df.dropna()
    print(f"✅ Valid rows after dropna: {len(df)}")

    return df


# ==========================================
# 2️⃣ LONG FORMAT (BOARD → ZONE)
# ==========================================
def prepare_long_format(df, feature_cols, zone_cols):
    X_raw = df[feature_cols].values           # (N, n_features)
    Y_raw = df[zone_cols].values              # (N, n_zones)

    n_samples, n_zones = Y_raw.shape

    # zone index: 1 → n_zones
    zone_idx = np.tile(np.arange(1, n_zones + 1), n_samples).reshape(-1, 1)
    zone_scaled = zone_idx / n_zones

    # repeat physical features for each zone
    X_long = np.repeat(X_raw, n_zones, axis=0)
    X_long = np.hstack([X_long, zone_scaled])

    Y_long = Y_raw.reshape(-1, 1)

    print(f"📊 Long-format X: {X_long.shape}, Y: {Y_long.shape}")
    return X_long, Y_long


# ==========================================
# 3️⃣ SCALING
# ==========================================
def scale_features(X, Y):
    x_scaler = StandardScaler()
    y_scaler = StandardScaler()

    X_scaled = x_scaler.fit_transform(X)
    Y_scaled = y_scaler.fit_transform(Y).ravel()

    return X_scaled, Y_scaled, x_scaler, y_scaler


# ==========================================
# 4️⃣ TRAIN XGBOOST
# ==========================================
def train_xgb(X_train, Y_train):
    model = XGBRegressor(
        n_estimators=600,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="reg:pseudohubererror",
        random_state=42,
        tree_method="hist"
    )

    print("🚀 Training XGBoost...")
    model.fit(X_train, Y_train)
    print("✅ Training done")

    return model


# ==========================================
# 5️⃣ EVALUATION
# ==========================================
def evaluate_model(model, X_test, Y_test, y_scaler):
    Y_pred_scaled = model.predict(X_test)

    Y_pred = y_scaler.inverse_transform(Y_pred_scaled.reshape(-1, 1)).ravel()
    Y_true = y_scaler.inverse_transform(Y_test.reshape(-1, 1)).ravel()

    mae = mean_absolute_error(Y_true, Y_pred)
    print(f"🎯 MAE: {mae:.3f} °C")

    return Y_true, Y_pred


# ==========================================
# 6️⃣ FEATURE IMPORTANCE & SHAP
# ==========================================
def plot_feature_importance(model, feature_names):
    fi = pd.DataFrame({
        "Feature": feature_names,
        "Importance": model.feature_importances_
    }).sort_values("Importance", ascending=False)

    print("\n📊 Feature importance:")
    print(fi)

    plt.figure(figsize=(8, 4))
    plt.barh(fi["Feature"], fi["Importance"])
    plt.gca().invert_yaxis()
    plt.title("Feature Importance – XGBoost")
    plt.tight_layout()
    plt.show()

    plot_importance(model, importance_type="gain", height=0.5)
    plt.title("Feature Importance (Gain)")
    plt.tight_layout()
    plt.show()


def shap_analysis(model, X_train, X_test, feature_names):
    print("\n💡 Computing SHAP values...")
    explainer = shap.Explainer(model, X_train, feature_names=feature_names)
    shap_values = explainer(X_test)

    shap.summary_plot(shap_values, X_test, feature_names=feature_names)
    shap.plots.waterfall(shap_values[0])


# ==========================================
# 7️⃣ PREDICT FULL PROFILE
# ==========================================
def predict_profile(model, x_phys, n_zones, x_scaler, y_scaler):
    zones = np.arange(1, n_zones + 1).reshape(-1, 1)
    zone_scaled = zones / n_zones

    X_pred = np.hstack([
        np.repeat(x_phys, n_zones, axis=0),
        zone_scaled
    ])

    Y_scaled = model.predict(x_scaler.transform(X_pred))
    Y_pred = y_scaler.inverse_transform(Y_scaled.reshape(-1, 1)).ravel()

    return Y_pred


# ==========================================
# 8️⃣ PLOT PROFILE
# ==========================================
def plot_profile(Y_true, Y_pred):
    plt.figure(figsize=(7, 4))
    plt.plot(range(1, 11), Y_true, "o-", label="Actual", linewidth=2)
    plt.plot(range(1, 11), Y_pred, "s--", label="Predicted", linewidth=2)

    plt.xlabel("Zone")
    plt.ylabel("Temperature (°C)")
    plt.title("Reflow Profile: Actual vs XGBoost")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# ==========================================
# 9️⃣ MAIN
# ==========================================
def main():
    # ---- Load data
    df = load_and_clean_data("summary.csv")

    # ---- Input features (ADD U HERE)
    feature_cols = [
        "x1", "x2", "x3", "x4",
        "x5", "x6", "x7", "x8",
        "Speed", "U"
    ]

    # ---- Output zones (10 zones)
    zone_cols = [f"zone {i}" for i in range(1, 11)]

    # ---- Long format
    X_long, Y_long = prepare_long_format(df, feature_cols, zone_cols)

    # ---- Scaling
    X_scaled, Y_scaled, x_scaler, y_scaler = scale_features(X_long, Y_long)

    # ---- Split
    X_train, X_test, Y_train, Y_test = train_test_split(
        X_scaled, Y_scaled, test_size=0.1, random_state=42
    )

    # ---- Train
    model = train_xgb(X_train, Y_train)

    # ---- Save
    joblib.dump(model, "xgb_model.pkl")
    joblib.dump(x_scaler, "xgb_x_scaler.pkl")
    joblib.dump(y_scaler, "xgb_y_scaler.pkl")

    # ---- Evaluate
    evaluate_model(model, X_test, Y_test, y_scaler)

    # ---- Explain
    feature_names = feature_cols + ["zone_index"]
    plot_feature_importance(model, feature_names)
    shap_analysis(model, X_train, X_test, feature_names)

    # ---- Predict one sample profile
    i = 0
    x_phys = df[feature_cols].values[i].reshape(1, -1)
    Y_pred_profile = predict_profile(
        model, x_phys, n_zones=10,
        x_scaler=x_scaler,
        y_scaler=y_scaler
    )
    Y_true_profile = df[zone_cols].values[i]

    plot_profile(Y_true_profile, Y_pred_profile)

    print("✅ DONE.")


if __name__ == "__main__":
    main()
