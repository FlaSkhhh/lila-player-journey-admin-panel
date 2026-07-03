# Architecture \& Technical Decisions



## Data Pipeline



To ensure the dashboard loads instantly for Level Designers, I separated the data processing from the UI rendering.

1. **Extraction:** `preprocess.py` reads the raw, line-delimited bytes(nakama-0) files.
2. **Transformation:** Applied World-to-Pixel math, categorized events, and sorted by timestamps.
3. **Loading:** Saved the cleaned dataset as a `.parquet` file. Streamlit caches this file in memory, reducing load times to almost instant.

## 

## Developer Tooling \& Data Verification



To ensure the visual UI accurately reflected the underlying math, I built a **"Download Match JSON"** export button directly into the active dashboard. Instead of forcing developers to dig through the raw backend logs, this tool allows engineers to instantly export the exact match data being viewed on the screen to a json file for cross-referencing events and timestamps.

## 

## Coordinate Mapping \& Image Standardization



The raw data provided 3D world coordinates, which do not map 1:1 with image pixels. Additionally, the minimap images were provided in wildly varying dimensions (from 9000x9000 down to 2160x2158) and in mixed file formats (jpg and png).

To guarantee the spatial math worked universally for each map:

1. I dynamically loaded and resized every minimap image to a strict 1024x1024 canvas in memory using PIL.
2. I applied the provided scale metrics to the World coordinates to normalize them to this 1024 grid:

   * `pixel\_x = ((world\_x - Origin\_X) / Scale) \* 1024`
   * `pixel\_y = ((world\_y - Origin\_Z) / Scale) \* 1024` (Note: Origin\_Z maps to the Y-axis).
3. I flipped the Y-axis in Plotly's layout (`range=\[1024, 0]`) to account for standard image coordinate systems (0,0 at top-left).

## 

## Edge Cases Handled



1. **The Timestamp Bug:** Unix timestamps (`ts`) were read by Pandas as nanoseconds, compressing 15-minute matches into fractions of a second. I explicitly cast `ts` using `unit='s'` to fix the timeline slider and normalize the data.
2. **UI Component Mismatches:** Streamlit's slider widget natively rejects Pandas `Timestamp` objects and will crash the UI. I had to explicitly isolate the min/max time bounds and cast them to native Python `datetime` objects to prevent the dashboard from freezing during timeline scrubbing.
3. **UI State Management (The "Bots Only" Bug):** Because the dataset contained heavily asymmetric lobbies (e.g., 1 Human / 0 Bots), applying a global "Bots Only" filter would completely delete the active match from the dataframe, causing Streamlit to abruptly auto-select a different match. I fixed this by shifting the filter down the pipeline—keeping the dropdown populated with *all* matches, and only applying the entity filter locally at the rendering step. This keeps the active match stable and gracefully renders a blank map if no bots are present.

## 

## Major Trade-offs



|Decision|Alternative Considered|Why I Chose This|
|-|-|-|
|**`mode='lines'` vs. `markers`**|Plotting individual dots for every frame.|Lines drastically reduce the number of SVG elements Plotly has to render, ensuring smooth WebGL performance.|
|**Parquet vs. SQLite/JSON**|Loading JSON directly into Streamlit.|Parquet preserves data types (like datetime) and reads 10x faster, enabling instant map filtering.|
|**Dynamic Dropdown vs. Calendar**|Using Streamlit's native `st.date\_input`.|The dataset contains dates from 10 Feb to 14 Feb. A calendar forces users to click blindly to find valid data. A dynamic dropdown populated only by `df\['date'].unique()` guarantees every user click has data for this assignment.|
|**Native Plotly Legend vs. UI Overlay**|Building custom Streamlit markdown text above the map.|By utilizing Plotly's native legend, I enabled the Legeng interactivity, allowing designers to click the legend to toggle it on/off directly inside the WebGL canvas.|
|**Python View Routing vs. CSS Tabs**|Using Streamlit's native `st.tabs`.|CSS tabs cause WebGL context-loss bugs in Plotly when switching views. Using Python radio buttons forces a clean redraw every time.|



