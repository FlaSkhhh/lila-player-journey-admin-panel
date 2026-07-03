# LILA BLACK - Player Journey Visualization Tool

A dedicated spatial analytics dashboard built for the Level Design Team to analyze player flow, combat hotspots, and human vs. bot behaviors.

## Tech Stack
* **Frontend UI & Framework:** Streamlit (Chosen for rapid prototyping and clean UI elements).
* **Visualizations:** Plotly Express & Graph Objects (Chosen for WebGL performance and interactive hover tooltips).
* **Data Processing:** Pandas & Parquet (Chosen for high-speed I/O and vectorized math).

## Setup & Local Installation

1. **Clone the repository.**
2. **Install dependencies:**
   `pip install streamlit pandas plotly pillow fastparquet`
3. **Data Pipeline (ETL):** If the `master_cleaned_data.parquet` file is not present, you must generate it from the raw `.bytes` files by running:
   `python preprocess.py`
4. **Run the Dashboard:**
   `streamlit run app.py`

## Key Features
* **ETL Pipeline:** Converts raw `.bytes` files, extracts JSON, maps 3D world coordinates to 2D image UV space, and compresses to Parquet.
* **Interactive Timeline:** Scrub through a match chronologically to observe pacing.
* **Dynamic Heatmaps:** Identifies choke points and killboxes.
* **Developer Tools:** Instantly export filtered match telemetry to JSON directly from the UI.