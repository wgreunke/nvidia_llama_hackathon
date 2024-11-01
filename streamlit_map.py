import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import datetime
import os

# Initialize session state for tracking clicked event
if 'clicked_event_index' not in st.session_state:
    st.session_state.clicked_event_index = None

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

# Add index column for click handling
filtered_events_df = filtered_events_df.reset_index(drop=True)

def map_click_handler(widget_instance, payload):
    if payload["type"] == "click" and payload["index"] is not None:
        st.session_state.clicked_event_index = payload["index"]
        st.experimental_rerun()

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
)

# Create the deck specification
view_state = pdk.ViewState(
    latitude=center_lat,
    longitude=center_lon,
    zoom=5,
    pitch=0,
)

# Create the deck specification
deck = pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=view_state,
    layers=[layer],
    tooltip={
        "html": "<b>{city}, {state}</b><br/>{event}<br/><i>Click for details</i>",
        "style": {
            "backgroundColor": "white",
            "color": "black",
            "fontSize": "0.8em",
            "padding": "5px"
        }
    }
)

# Display the map with click handling
st.pydeck_chart(
    deck,
    use_container_width=True,
    on_click=map_click_handler
)

# Get the event index either from click or dropdown
selected_event_index = st.session_state.clicked_event_index

# Only show dropdown if no event is selected by clicking
if selected_event_index is None:
    event_options = [f"{row['city']}, {row['state']} - {row['event']}" for _, row in filtered_events_df.iterrows()]
    selected_event_index = st.selectbox(
        "Or select an event from the list:",
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
        
        # Add a close button at the top right
        if st.button("✖ Close Details", key="close_details"):
            st.session_state.clicked_event_index = None
            st.experimental_rerun()
        
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
