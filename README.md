# 53' Dry Van Freight Rate Predictor

[![Streamlit App](https://img.shields.io/badge/Launch-App-brightgreen?logo=streamlit)](https://freight-rater-53.streamlit.app/)


📦 Adding Your Own Internal Freight Data for More Accurate Predictions

This project ships with a synthetic dataset to demonstrate the end-to-end machine-learning workflow.
However, the model is designed so that any brokerage, carrier, shipper, or analyst can plug in their own historical freight data to dramatically improve prediction accuracy on real lanes.

Below is a guide on how to prepare and integrate internal data safely and effectively.

✅ 1. Required Data Fields

Your internal dataset should include the following:

Field	Description
origin_city	Origin city or ZIP code
destination_city	Destination city or ZIP code
miles	Routed or practical miles for the load
diesel_price	Diesel index at time of pickup (optional — the system can fill it in automatically)
pickup_date	Shipment pickup date
rate	The actual buy rate or sell rate for the load
Optional (but highly valuable):
Field	Why it helps
equipment_type	Enables multi-equipment prediction (van, reefer, flatbed, etc.)
weight	Impacts pricing, especially on shorter lanes
lead_time_days	Pickup lead time strongly correlates with rate volatility
market_index	SONAR/MDI-style features if your organization licenses them
season	Captures quarterly/seasonal variance

Adding these features significantly improves prediction stability.

✅ 2. How to Format Your Dataset

Place your cleaned CSV file in the project’s data/ directory:

/data/internal_freight_data.csv


Example:

origin_city,destination_city,miles,diesel_price,pickup_date,rate
Chicago,IL,716,4.12,2024-11-04,1150
Dallas,TX,420,3.98,2024-10-12,780
Los Angeles,CA,1980,4.06,2024-09-30,3350

✅ 3. Using Internal Data Instead of Synthetic Data

To train the model on your actual lane history:

Open train_model.py

Replace:

df = build_training_dataframe()


with:

import pandas as pd
df = pd.read_csv("data/internal_freight_data.csv")


Make sure your columns match the fields the model expects.

Retrain:

python train_model.py


This produces a new model.pkl trained entirely on your internal dataset.

✅ 4. Automatic Data Enrichment

If your internal dataset does not include certain fields, the system fills them in:

Missing diesel price?

The app automatically fetches the correct diesel index for each record using the EIA API.

Missing miles?

The app automatically calls OpenRouteService (ORS) to compute actual routed mileage.

Using ZIP codes instead of city names?

ORS handles both seamlessly — no preprocessing required.

This means your dataset can be fairly raw, and the system will enhance it automatically.

✅ 5. Data Privacy Best Practices

Before integrating internal data, it’s recommended to remove:

Customer names

Carrier names

Account identifiers

Shipment IDs

Emails or notes

Rate confirmation documents

Keep only lane-level numeric and geographic features.
This prevents leaking sensitive or commercially identifiable information.

✅ 6. Retraining Frequency

For active freight networks, organizations typically retrain:

Weekly for high-volume lanes

Monthly for long-haul or seasonal lanes

On-demand when market conditions shift

Each retrain overwrites the existing model.pkl, and the Streamlit app immediately starts using the updated model.

📈 Summary

By loading your organization’s internal freight history into this project, you transform it from a synthetic demo into a true predictive pricing engine capable of producing accurate, lane-specific dry van, reefer, or flatbed rates.

This turns the project into a customizable, data-driven freight-tech tool ready for real-world use.
