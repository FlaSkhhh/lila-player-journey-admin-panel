import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import os

# 1. Page Configuration & Layout Customization
st.set_page_config(
    page_title="LILA BLACK - Player Journey Tool",
    page_icon="🎯",
    layout="wide"
)

st.title("LILA ASSIGNMENT - Player Journey Visualization Tool")
st.caption("A dedicated spatial analytics dashboard for the Level Design Team.")
st.markdown("---")

# 2. Optimized Data Loading with Streamlit Caching
@st.cache_data
def load_master_data():
    if not os.path.exists("master_cleaned_data.parquet"):
        st.error("Error: 'master_cleaned_data.parquet' not found! Please run preprocess.py first.")
        st.stop()
        
    df = pd.read_parquet("master_cleaned_data.parquet")
    
    # THE TIME FIX
    if pd.api.types.is_datetime64_any_dtype(df['ts']):
        df['ts'] = pd.to_datetime(df['ts'].astype('int64'), unit='s')
    else:
        df['ts'] = pd.to_datetime(df['ts'], unit='s')
        
    return df

df = load_master_data()

# 3. Sidebar Filtering Options
st.sidebar.header("Global Map & Target Filters")

# Map Selection
map_options = sorted(df['map_id'].unique())
selected_map = st.sidebar.selectbox("Select Map Environment", map_options)
map_df = df[df['map_id'] == selected_map]

# Date Filter (Applied Globally)
map_df['date'] = map_df['ts'].dt.date
date_options = sorted(map_df['date'].unique())
selected_date = st.sidebar.selectbox("Filter by Date", ["All Dates"] + date_options)
if selected_date != "All Dates":
    map_df = map_df[map_df['date'] == selected_date]

# Player Type Toggle (We capture the setting here, but apply it later!)
player_type = st.sidebar.radio("Player Category", ["All", "Humans Only", "Bots Only"])

st.sidebar.markdown("---")

# Dashboard View Routing 
view_mode = st.sidebar.radio(
    "Select Dashboard View", 
    ["Match Timeline Playback", "Heatmap Aggregates"]
)
    
# 4. Image Loader Utility
def load_minimap_image(map_name):
    ext = "jpg" if map_name == "Lockdown" else "png"
    img_path = f"player_data/minimaps/{map_name}_Minimap.{ext}"
    try:
        img = Image.open(img_path)
        return img.resize((1024, 1024))
    except Exception:
        st.error(f"Could not load minimap image at: {img_path}. Verify your folder structure.")
        return None

minimap_img = load_minimap_image(selected_map)


# ----------------------------------------------------
# VIEW 1: MATCH TIMELINE PLAYBACK
# ----------------------------------------------------
if view_mode == "Match Timeline Playback":
    st.subheader("Interactive Match Timeline Explorer")
    st.markdown("Use the playback slider below to step through time and watch individual journeys unfold.")

    if not map_df.empty and minimap_img:
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            sort_order = st.radio("Match List Sort Order", ["Chronological", "Alphabetical"], horizontal=True)
            
            if sort_order == "Chronological":
                match_start_times = map_df.groupby('match_id')['ts'].min().sort_values()
                match_options = match_start_times.index.tolist()
            else:
                match_options = sorted(map_df['match_id'].unique())
            
            # UX UPGRADE: Show human/bot counts in the dropdown so Level Designers aren't guessing
            player_counts = map_df.groupby(['match_id', 'is_bot'])['user_id'].nunique().unstack(fill_value=0)
            if False not in player_counts.columns: player_counts[False] = 0
            if True not in player_counts.columns: player_counts[True] = 0
            
            def get_match_label(mid):
                h_count = player_counts.loc[mid, False] if mid in player_counts.index else 0
                b_count = player_counts.loc[mid, True] if mid in player_counts.index else 0
                return f"{mid} ({h_count} Humans | {b_count} Bots)"

            selected_match = st.selectbox(
                f"Select Match ID (Found {len(match_options)} matches)", 
                options=match_options,
                format_func=get_match_label 
            )
            
            # 1. Grab the base match
            match_df = map_df[map_df['match_id'] == selected_match]

            # 2. NOW apply the Player Category filter specifically to this match view
            if player_type == "Humans Only":
                match_df = match_df[match_df['is_bot'] == False]
            elif player_type == "Bots Only":
                match_df = match_df[match_df['is_bot'] == True]

        with col2:
            st.markdown("<br>", unsafe_allow_html=True) 
            json_data = match_df.to_json(orient="records", date_format="iso")
            st.download_button("📥 Download Match JSON", json_data, f"{selected_match}_telemetry.json", "application/json")      

        # 3. Safe Check: If the filter resulted in an empty map (e.g. 0 bots), draw a blank map and skip the slider
        if match_df.empty:
            st.warning(f"No data available for '{player_type}' in this specific match. Please select a different match or category.")
            fig = px.imshow(minimap_img)
            fig.update_layout(width=900, height=900, xaxis=dict(visible=False, range=[0, 1024]), yaxis=dict(visible=False, range=[1024, 0]), margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            # Timeline Slider control
            min_dt = match_df['ts'].min().to_pydatetime()
            max_dt = match_df['ts'].max().to_pydatetime()
            
            if min_dt == max_dt:
                max_dt = min_dt + datetime.timedelta(seconds=1)
            
            selected_time = st.slider(
                "Match Timeline Playback",
                min_value=min_dt, max_value=max_dt, value=max_dt,
                step=datetime.timedelta(seconds=5), format="YYYY-MM-DD HH:mm:ss"        
            )

            # Slice data
            timeline_df = match_df[match_df['ts'] <= selected_time]

            is_position_event = timeline_df['event'].isin(['Position', 'BotPosition'])
            paths_df = timeline_df[is_position_event]
            events_df = timeline_df[~is_position_event]

           # Generate base figure using the minimap image asset
            fig = px.imshow(minimap_img)

            # Draw player movement trails AND Spawn Points
            added_human, added_bot = False, False
            for player_id, p_group in paths_df.groupby('user_id'):
                p_group = p_group.sort_values('ts') 
                is_bot = p_group['is_bot'].iloc[0]
                color = "#00F0FF" if is_bot else "#FF4B4B"
                name_label = "Bot Paths" if is_bot else "Human Paths"
                
                show_in_legend = False
                if is_bot and not added_bot: show_in_legend, added_bot = True, True
                elif not is_bot and not added_human: show_in_legend, added_human = True, True
                
                # 1. NEW: Draw the Spawn Point (Starting Circle)
                fig.add_trace(go.Scatter(
                    x=[p_group['pixel_x'].iloc[0]], 
                    y=[p_group['pixel_y'].iloc[0]], 
                    mode='markers',
                    marker=dict(size=12, color=color, line=dict(width=2, color='white')),
                    name=f"Spawn ({name_label})",
                    legendgroup="bots" if is_bot else "humans", 
                    showlegend=False, # Kept out of legend to avoid clutter
                    hoverinfo='text',
                    text=f"Player: {player_id}<br>Event: Spawn Drop<br>Time: {p_group['ts'].iloc[0].strftime('%H:%M:%S')}"
                ))

                # 2. Draw the continuous path
                fig.add_trace(go.Scatter(
                    x=p_group['pixel_x'], y=p_group['pixel_y'], mode='lines',
                    line=dict(width=2, color=color), name=name_label,
                    legendgroup="bots" if is_bot else "humans", showlegend=show_in_legend,
                    hoverinfo='text',
                    text=[f"Player: {player_id}<br>Event: {e}<br>Time: {t.strftime('%H:%M:%S')}" for e, t in zip(p_group['event'], p_group['ts'])]
                ))

            event_emojis = {'Kill': '🎯', 'Killed': '☠️', 'BotKill': '🤖', 'BotKilled': '🪫', 'Loot': '💰', 'KilledByStorm': '🌩️'}

            for event_type, e_group in events_df.groupby('event'):
                if event_type in event_emojis:
                    fig.add_trace(go.Scatter(
                        x=e_group['pixel_x'], y=e_group['pixel_y'], mode='text',
                        # --- UPGRADED: Increased emoji size from 14 to 24 ---
                        text=[event_emojis[event_type]] * len(e_group), textfont=dict(size=24),          
                        name=f"{event_emojis[event_type]} {event_type}", showlegend=True,
                        hoverinfo='text', hovertext=[f"Player: {uid}<br>Event: {event_type}" for uid in e_group['user_id']] 
                    ))

            fig.update_layout(width=900, height=900, xaxis=dict(visible=False, range=[0, 1024]), yaxis=dict(visible=False, range=[1024, 0]), margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="v", yanchor="top", y=0.98, xanchor="left", x=0.02, bgcolor="rgba(0,0,0,0.6)", font=dict(color="white")))
            st.plotly_chart(fig, use_container_width=True)


# ----------------------------------------------------
# VIEW 2: HEATMAP AGGREGATES
# ----------------------------------------------------
elif view_mode == "Heatmap Aggregates":
    st.subheader("Spatial Hotspot Density Analysis")
    st.markdown("Analyzes aggregate behaviors across **all matches** matching your chosen sidebar criteria.")

    if not map_df.empty and minimap_img:
        heatmap_metric = st.selectbox(
            "Select Heatmap Mode",
            ["High-Traffic (Movement Positions)", "Kill Zones", "Death Zones", "Loot Distribution"]
        )    

        # Apply the Player Category filter to the Heatmaps specifically
        heatmap_df = map_df.copy()
        if player_type == "Humans Only":
            heatmap_df = heatmap_df[heatmap_df['is_bot'] == False]
        elif player_type == "Bots Only":
            heatmap_df = heatmap_df[heatmap_df['is_bot'] == True]

       # Filter based on analysis selection
        if heatmap_metric == "High-Traffic (Movement Positions)":
            target_df = heatmap_df[heatmap_df['event'].isin(['Position', 'BotPosition'])]
            if selected_map == "GrandRift":
                colorscale = [[0, 'rgba(255,0,255,0)'], [0.2, 'rgba(200,0,255,0.6)'], [1, 'rgba(138,43,226,0.9)']]
            elif selected_map == "Lockdown":
                colorscale = [[0, 'rgba(255,20,147,0)'], [0.2, 'rgba(255,105,180,0.6)'], [1, 'rgba(255,0,255,0.9)']]
            else: # AmbroseValley
                colorscale = [[0, 'rgba(255,165,0,0)'], [0.2, 'rgba(255,140,0,0.5)'], [1, 'rgba(255,255,0,0.8)']]
                
        elif heatmap_metric == "Kill Zones":
            target_df = heatmap_df[heatmap_df['event'].isin(['Kill', 'BotKill'])]
            if selected_map == "GrandRift":
                colorscale = [[0, 'rgba(0,255,255,0)'], [0.2, 'rgba(0,191,255,0.6)'], [1, 'rgba(0,0,255,0.9)']]
            elif selected_map == "Lockdown":
                colorscale = [[0, 'rgba(255,215,0,0)'], [0.2, 'rgba(255,140,0,0.6)'], [1, 'rgba(255,69,0,0.9)']]
            else: # AmbroseValley
                colorscale = [[0, 'rgba(0,255,255,0)'], [0.2, 'rgba(0,206,209,0.6)'], [1, 'rgba(0,128,128,0.9)']]

        elif heatmap_metric == "Death Zones":
            target_df = heatmap_df[heatmap_df['event'].isin(['Killed', 'BotKilled', 'KilledByStorm'])]
            if selected_map == "GrandRift":
                colorscale = [[0, 'rgba(255,0,255,0)'], [0.2, 'rgba(255,20,147,0.6)'], [1, 'rgba(139,0,139,0.9)']]
            else:
                colorscale = [[0, 'rgba(255,0,0,0)'], [0.2, 'rgba(255,0,0,0.6)'], [1, 'rgba(139,0,0,0.9)']]
         
        else: # Loot Distribution
            target_df = heatmap_df[heatmap_df['event'] == 'Loot']
            if selected_map == "Lockdown":
                colorscale = [[0, 'rgba(255,215,0,0)'], [0.2, 'rgba(255,223,0,0.6)'], [1, 'rgba(218,165,32,0.9)']]
            elif selected_map == "GrandRift":
                colorscale = [[0, 'rgba(0,255,0,0)'], [0.2, 'rgba(50,205,50,0.6)'], [1, 'rgba(0,128,0,0.9)']]
            else: # AmbroseValley
                colorscale = [[0, 'rgba(0,255,0,0)'], [0.2, 'rgba(50,205,50,0.6)'], [1, 'rgba(0,255,0,0.9)']]

        if not target_df.empty:
            heat_fig = go.Figure(data=go.Histogram2dContour(
                x=target_df['pixel_x'],
                y=target_df['pixel_y'],
                colorscale=colorscale,
                ncontours=20,
                showscale=False,
                xbins=dict(start=0, end=1024, size=16),
                ybins=dict(start=0, end=1024, size=16),
                contours=dict(coloring='fill')
            ))
            
            heat_fig.add_layout_image(
                dict(
                    source=minimap_img,
                    xref="x", yref="y",
                    x=0, y=0,
                    sizex=1024, sizey=1024,
                    sizing="stretch",
                    layer="below"
                )
            )

            heat_fig.update_layout(
                width=900,
                height=900,
                xaxis=dict(visible=False, range=[0, 1024]),
                yaxis=dict(visible=False, range=[1024, 0]),
                margin=dict(l=0, r=0, t=10, b=0),
                plot_bgcolor='rgba(0,0,0,0)',  
                paper_bgcolor='rgba(0,0,0,0)'  
            )

            st.plotly_chart(heat_fig, use_container_width=True)
        else:
            st.info("No matching target records discovered for the selected tracking matrix metric.")