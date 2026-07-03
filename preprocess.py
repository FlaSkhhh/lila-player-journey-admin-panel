import os
import pandas as pd
import pyarrow.parquet as pq
from pathlib import Path

# Map configurations based on the provided data schema
MAP_CONFIGS = {
    'AmbroseValley': {'scale': 900, 'origin_x': -370, 'origin_z': -473},
    'GrandRift': {'scale': 581, 'origin_x': -290, 'origin_z': -290},
    'Lockdown': {'scale': 1000, 'origin_x': -500, 'origin_z': -500}
}

def process_telemetry_data(data_dir: str, output_file: str):
    """
    Scans for raw .nakama-0 files, cleans the data, calculates 2D pixel coordinates, 
    and exports a single optimized .parquet file.
    """
    print(f"Scanning directory: {data_dir} for match files...")

    # 1. Recursively gather all raw player files
    all_files = list(Path(data_dir).rglob("*.nakama-0"))
    if not all_files:
        print(f"Error: No '.nakama-0' files found in {data_dir}.")
        return

    print(f"Found {len(all_files)} files. Extracting and combining...")

    # 2. Load and concatenate
    df_list = []
    for file in all_files:
        try:
            table = pq.read_table(file)
            df_list.append(table.to_pandas())
        except Exception as e:
            print(f"Failed to read {file}: {e}")

    master_df = pd.concat(df_list, ignore_index=True)
    print(f"Successfully compiled {len(master_df):,} event rows.")

    # 3. Clean and Decode Data
    print("Decoding byte streams and categorizing player types...")
    # Decode 'event' column from bytes to string safely
    master_df['event'] = master_df['event'].apply(
        lambda x: x.decode('utf-8') if isinstance(x, bytes) else str(x)
    )
    
    # Identify Bots vs Humans: Bots use short numeric IDs, Humans use UUIDs
    master_df['is_bot'] = master_df['user_id'].str.isnumeric()

    # 4. Map 3D World Coordinates to 2D Minimap Pixels (Vectorized)
    print("Calculating UVs and translating to 1024x1024 minimap pixels...")
    
    # Merge the map configurations into the dataframe for fast vectorized math
    config_df = pd.DataFrame.from_dict(MAP_CONFIGS, orient='index')
    master_df = master_df.join(config_df, on='map_id')

    # Drop rows where map_id is missing or unrecognized to prevent math errors
    master_df = master_df.dropna(subset=['scale'])

    # Step 1: Convert world coords to UV (0-1 range)
    u = (master_df['x'] - master_df['origin_x']) / master_df['scale']
    v = (master_df['z'] - master_df['origin_z']) / master_df['scale']

    # Step 2: Convert UV to pixel coords (1024x1024 image space, flipping Y)
    master_df['pixel_x'] = u * 1024
    master_df['pixel_y'] = (1 - v) * 1024

    # Clean up calculation columns to keep the final dataframe lightweight
    master_df.drop(columns=['origin_x', 'origin_z', 'scale'], inplace=True)

    # 5. Optimize and Export
    print(f"Exporting master dataset to {output_file}...")
    
    # Sorting by match_id and timestamp ensures the Streamlit playback slider runs smoothly
    master_df.sort_values(by=['match_id', 'ts'], inplace=True)
    
    master_df.to_parquet(output_file, engine='pyarrow', index=False)
    print("ETL Pipeline Complete! The data is ready for the visualization frontend.")


if __name__ == "__main__":
    # Define paths relative to where the script is run
    # Assuming 'player_data' folder is in the same directory as this script
    RAW_DATA_DIRECTORY = "./player_data"
    CLEANED_DATA_OUTPUT = "./master_cleaned_data.parquet"

    process_telemetry_data(RAW_DATA_DIRECTORY, CLEANED_DATA_OUTPUT)