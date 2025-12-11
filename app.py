import datetime
import os
import joblib
import streamlit as st
import traceback

from utils.api_calls import (
    get_distance_miles,
    get_diesel_price,         # <-- correct function name
    get_route_geometry,
    ApiError
)
from utils.feature_engineering import build_feature_vector

MODEL_PATH = "model.pkl"


@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model not found. Run train_model.py first.")
    return joblib.load(MODEL_PATH)


def main():
    st.title("53' Dry Van Freight Rate Predictor")

    # ------------------------------------------------
    # Sidebar Inputs
    # ------------------------------------------------
    st.sidebar.header("Lane Inputs")
    origin = st.sidebar.text_input("Origin", "Chicago, IL")
    destination = st.sidebar.text_input("Destination", "Atlanta, GA")
    pickup_date = st.sidebar.date_input("Pickup Date", datetime.date.today())

    # IMPORTANT: button must be outside any container to keep state stable
    predict = st.sidebar.button("Predict Rate")

    # Load model once
    model = load_model()

    # Stable container so Streamlit does not erase the output on rerun
    result_box = st.container()

    # ------------------------------------------------
    # Prediction Logic
    # ------------------------------------------------
    if predict:
        try:
            # 1. Distance calculation
            with st.spinner("Calculating distance..."):
                distance_miles = get_distance_miles(origin, destination)

            # 2. Diesel price (from updated API)
            diesel_price = get_diesel_price()

            # 3. Build model input
            features = build_feature_vector(distance_miles, diesel_price, pickup_date)

            # 4. ML prediction
            predicted_rate = model.predict(features)[0]
            rpm = predicted_rate / max(distance_miles, 1e-6)

            # 5. Get route geometry for map
            geometry = get_route_geometry(origin, destination)

            # ------------------------------------------------
            # Display Results
            # ------------------------------------------------
            with result_box:
                st.subheader("Predicted 53' Dry Van Rate")
                st.write(f"**Total Rate:** ${predicted_rate:,.2f}")
                st.write(f"**Rate per Mile:** ${rpm:.2f}")

                # Map
                if geometry is not None:
                    st.subheader("Route Map")
                    st.map(geometry)

                # Details
                with st.expander("Details"):
                    st.write(f"Distance: {distance_miles:.1f} miles")
                    st.write(f"Diesel Price: ${diesel_price:.2f}")
                    st.write(f"Pickup Date: {pickup_date}")

        except ApiError as e:
            st.error(f"API error: {e}")

        except Exception as e:
            st.error(f"Unexpected error: {e}")
            st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
