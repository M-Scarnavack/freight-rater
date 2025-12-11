import os
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

from utils.feature_engineering import build_training_dataframe

DATA_DIR = "data"
MODEL_PATH = "model.pkl"


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    # Generate synthetic data
    df = build_training_dataframe(n_samples=3000, random_state=42)
    csv_path = os.path.join(DATA_DIR, "synthetic_freight_data.csv")
    df.to_csv(csv_path, index=False)

    # Define features
    feature_cols = ["distance_miles", "diesel_price", "month", "dow"]

    X = df[feature_cols]
    y = df["total_rate"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Evaluate model
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = mse ** 0.5

    print(f"MAE:  {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")

    # Save model
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()

