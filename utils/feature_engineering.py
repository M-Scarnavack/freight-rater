import datetime
import numpy as np
import pandas as pd

# Only one equipment type for the project
EQUIPMENT_TYPES = ["Van"]


def extract_date_features(pickup_date: datetime.date) -> list[float]:
    """
    Extract month and day-of-week as numerical features.
    """
    month = float(pickup_date.month)
    dow = float(pickup_date.weekday())  # Monday = 0
    return [month, dow]


def build_feature_vector(distance_miles: float,
                         diesel_price: float,
                         pickup_date: datetime.date) -> np.ndarray:
    """
    Build a feature vector matching the model's expected columns:
    [distance_miles, diesel_price, month, dow]
    """
    month, dow = extract_date_features(pickup_date)

    features = [
        float(distance_miles),
        float(diesel_price),
        month,
        dow
    ]

    return np.array(features, dtype=float).reshape(1, -1)


def build_training_dataframe(n_samples: int = 3000, random_state: int = 42) -> pd.DataFrame:
    """
    Create synthetic freight data for 53' Dry Van only.
    This avoids proprietary data and allows model training.
    """

    rng = np.random.default_rng(random_state)

    # Random distances (miles)
    distances = rng.uniform(100, 2500, size=n_samples)

    # Diesel prices
    diesel_prices = rng.uniform(2.5, 5.5, size=n_samples)

    # Month (1–12) and day of week (0–6)
    months = rng.integers(1, 13, size=n_samples)
    dows = rng.integers(0, 7, size=n_samples)

    # Seasonal effect (mild sinusoidal seasonal variation)
    seasonal_factor = 1.0 + 0.1 * np.sin((months - 1) / 12 * 2 * np.pi)

    # Base rate per mile (rpm) influenced by diesel price & seasonality
    base_rpm = 1.8 + 0.1 * (diesel_prices - 3.5)  # fuel cost effect
    rate_per_mile = base_rpm * seasonal_factor

    # Random noise for realism
    noise = rng.normal(0, 0.15, size=n_samples)

    # Total rate = miles × rpm + noise
    total_rate = distances * (rate_per_mile + noise)

    df = pd.DataFrame({
        "distance_miles": distances,
        "diesel_price": diesel_prices,
        "month": months,
        "dow": dows,
        "total_rate": total_rate
    })

    return df
