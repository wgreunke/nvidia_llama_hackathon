import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import datetime
import os
import json

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

# Create a unique ID for each point that we can use to identify clicks
filtered_events_df['point_id'] = range(len(filtered_events_df))

# Create the PyDeck layer
layer = pdk.Layer(
    "ScatterplotLayer",
    filtered_events_df,
    get_position=['lon', 'lat'],
    get_radius=20000,
    get_fill_color=[0, 68, 255],
    pickable=True,
    auto_highlight=True,
    radius_scale=3,
    radius_min_pixels=5,
    radius_max_pixels=15,
    onClick="function(info) { window.selectedPointId = info.object.point_id; document.dispatchEvent(new CustomEvent('deck_click')); }"
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
        "html": "<b>Click for details</b><br/>{city}, {state}",
        "style": {
            "backgroundColor": "white",
            "color": "black"
        }
    }
)

# Display the map
st.pydeck_chart(deck)

# Create a selectbox for event selection (as a fallback interaction method)
event_options = [f"{row['city']}, {row['state']} - {row['event']}" for _, row in filtered_events_df.iterrows()]
selected_event_index = st.selectbox(
    "Select an event to view details:",
    range(len(event_options)),
    format_func=lambda x: event_options[x],
    key='event_selector'
)

# Display selected event details
if selected_event_index is not None:
    selected_event = filtered_events_df.iloc[selected_event_index]
    
    # Create a card-like container for the details
    with st.container():
        st.markdown("---")  # Horizontal line for visual separation
        
        # Create columns for layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header(f"{selected_event['city']}, {selected_event['state']}")
            st.subheader(selected_event['event'])
            st.write(f"**Date:** {selected_event['date-of-event'].strftime('%B %d, %Y')}")
            st.write("**Summary:**")
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
                    st.write("Image URL:", selected_event['event-picture-link'])

# Optional: Display all events in a table below
with st.expander("View All Events"):
    st.dataframe(
        filtered_events_df[[
            'city', 'state', 'event', 'date-of-event', 'summary'
        ]]
    )
