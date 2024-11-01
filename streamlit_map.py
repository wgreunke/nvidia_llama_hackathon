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

# Date slider setup
min_date = events_df['date-of-event'].min().to_pydatetime().date()
max_date = events_df['date-of-event'].max().to_pydatetime().date()
initial_date = events_df['date-of-event'].min().to_pydatetime().date()

if min_date == max_date:
    max_date = max_date + datetime.timedelta(days=5)

selected_date = st.slider(
    'Select a date to filter events before this date',
    min_value='2024-09-20',
    max_value=max_date,
    value=initial_date,
    format="YYYY-MM-DD"
)

# Filter events based on selected date
selected_date = pd.Timestamp(selected_date)
filtered_events_df = events_df[events_df['date-of-event'] <= selected_date]

# Create tooltip column for hover information
filtered_events_df['tooltip'] = filtered_events_df.apply(
    lambda row: f"{row['city']}, {row['state']}\n{row['event']}", axis=1
)

# Calculate the center of the map
center_lat = filtered_events_df['lat'].mean()
center_lon = filtered_events_df['lon'].mean()

# Create the PyDeck layer
layer = pdk.Layer(
    "ScatterplotLayer",
    filtered_events_df,
    get_position=['lon', 'lat'],
    get_radius=10000,  # Size of the points
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
        "html": "<b>City:</b> {city}, {state}<br/>"
                "<b>Event:</b> {event}<br/>"
                "<b>Date:</b> {date-of-event}<br/>"
                "<b>Summary:</b> {summary}",
        "style": {
            "backgroundColor": "white",
            "color": "black"
        }
    }
)

# Display the map
st.pydeck_chart(deck)

# Create a section for detailed event information
st.subheader("Event Details")
for _, event in filtered_events_df.iterrows():
    with st.expander(f"{event['city']}, {event['state']} - {event['event']}"):
        st.write(f"**Date:** {event['date-of-event']}")
        st.write(f"**Summary:** {event['summary']}")
        if pd.notna(event['event-picture-link']):
            st.image(event['event-picture-link'], 
                    caption=event['event-picture-caption'] if pd.notna(event['event-picture-caption']) else None)
