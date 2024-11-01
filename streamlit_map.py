import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import datetime
import os

# Load and prepare the data
csv_file_name = "events.csv"
path = ""
events_df = pd.read_csv(os.path.join(path, csv_file_name))
events_df['date-of-event'] = pd.to_datetime(events_df['date-of-event'])

# Initialize session state for selected event
if 'selected_event_index' not in st.session_state:
    st.session_state.selected_event_index = None

# Date slider setup
min_date = events_df['date-of-event'].min().to_pydatetime().date()
max_date = events_df['date-of-event'].max().to_pydatetime().date()
initial_date = events_df['date-of-event'].min().to_pydatetime().date()

if min_date == max_date:
    max_date = max_date + datetime.timedelta(days=5)

selected_date = st.slider(
    'Select a date to filter events before this date',
    min_value=min_date,
    max_value=max_date,
    value=initial_date,
    format="YYYY-MM-DD"
)

# Filter events based on selected date
selected_date = pd.Timestamp(selected_date)
filtered_events_df = events_df[events_df['date-of-event'] <= selected_date]

# Calculate the center of the map
center_lat = filtered_events_df['lat'].mean()
center_lon = filtered_events_df['lon'].mean()

# Create the PyDeck layer
layer = pdk.Layer(
    "ScatterplotLayer",
    filtered_events_df,
    get_position=['lon', 'lat'],
    get_radius=20000,  # Size of the points
    get_fill_color=[0, 68, 255],  # Blue color
    pickable=True,  # Enable clicking
    auto_highlight=True,
    radius_scale=3,
    radius_min_pixels=5,
    radius_max_pixels=15,
)

# Create the deck specification
deck = pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=5,
        pitch=0,
    ),
    layers=[layer],
    tooltip={
        "html": "Click for details",
        "style": {
            "backgroundColor": "white",
            "color": "black"
        }
    }
)

# Handle click events
def handle_click(event):
    if event and event.object:
        index = event.index
        st.session_state.selected_event_index = index
        st.experimental_rerun()

# Display the map with click handling
st.pydeck_chart(deck, on_click=handle_click)

# Display selected event details
if st.session_state.selected_event_index is not None:
    selected_event = filtered_events_df.iloc[st.session_state.selected_event_index]
    
    # Create columns for layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header(f"{selected_event['city']}, {selected_event['state']}")
        st.subheader(selected_event['event'])
        st.write(f"**Date:** {selected_event['date-of-event'].strftime('%B %d, %Y')}")
        st.write(f"**Summary:**")
        st.write(selected_event['summary'])
    
    with col2:
        if pd.notna(selected_event['event-picture-link']):
            try:
                st.image(
                    selected_event['event-picture-link'],
                    caption=selected_event['event-picture-caption'] if pd.notna(selected_event['event-picture-caption']) else None,
                    use_column_width=True
                )
            except Exception as e:
                st.error("Unable to load image")

    # Add a close button
    if st.button('Close Details'):
        st.session_state.selected_event_index = None
        st.experimental_rerun()

# Optional: Display all events in a table below
with st.expander("View All Events"):
    st.dataframe(
        filtered_events_df[[
            'city', 'state', 'event', 'date-of-event', 'summary'
        ]]
    )
