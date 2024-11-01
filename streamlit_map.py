
import streamlit as st
import pandas as pd
import pydeck as pdk
import datetime
import os

# Page config
st.set_page_config(layout="wide", page_title="Hurricane Event Tracker")

# Initialize session state
if 'clicked_event_index' not in st.session_state:
    st.session_state.clicked_event_index = None

# Load and prepare the data
@st.cache_data
def load_data():
    events_df = pd.read_csv("events.csv")
    events_df['date-of-event'] = pd.to_datetime(events_df['date-of-event'])
    return events_df

events_df = load_data()

# Date slider setup
min_date = events_df['date-of-event'].min().to_pydatetime().date()
max_date = events_df['date-of-event'].max().to_pydatetime().date()

# Ensure min and max dates are different
if min_date == max_date:
    max_date = max_date + datetime.timedelta(days=1)

selected_date = st.slider(
    'Filter events before:',
    min_value=min_date,
    max_value=max_date,
    value=max_date,
    format="MMM DD, YYYY"
)

# Filter events based on selected date
filtered_events_df = events_df[events_df['date-of-event'].dt.date <= selected_date].copy()
filtered_events_df = filtered_events_df.reset_index(drop=True)

# Map creation
def create_map(data_df):
    center_lat = data_df['lat'].mean()
    center_lon = data_df['lon'].mean()
    
    layer = pdk.Layer(
        "ScatterplotLayer",
        data_df,
        get_position=["lon", "lat"],
        get_radius=20000,
        get_fill_color=[255, 0, 0, 140],  # Red with some transparency
        pickable=True,
        auto_highlight=True,
        radius_min_pixels=8,
        radius_max_pixels=15,
    )

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=5.5,
        pitch=0
    )

    return pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/light-v9",
        tooltip={
            "html": "<b>{city}, {state}</b><br/>{event}<br/><i>Click to view details</i>",
            "style": {
                "backgroundColor": "white",
                "color": "black"
            }
        }
    )

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    # Display the map
    deck = create_map(filtered_events_df)
    
    deck_data = st.pydeck_chart(
        deck,
        use_container_width=True,
    )
    
    if st.session_state.get("selected_point_index") is not None:
        st.session_state.clicked_event_index = st.session_state.selected_point_index
        st.session_state.selected_point_index = None

with col2:
    # Event selection
    if st.session_state.clicked_event_index is None:
        event_options = [f"{row['city']}, {row['state']} - {row['event']}" 
                        for _, row in filtered_events_df.iterrows()]
        if event_options:
            selected_index = st.selectbox(
                "Select an event:",
                range(len(event_options)),
                format_func=lambda x: event_options[x]
            )
            if st.button("Show Details"):
                st.session_state.clicked_event_index = selected_index

    # Display event details
    if st.session_state.clicked_event_index is not None and len(filtered_events_df) > st.session_state.clicked_event_index:
        event = filtered_events_df.iloc[st.session_state.clicked_event_index]
        
        # Close button
        if st.button("✖ Close", key="close_details"):
            st.session_state.clicked_event_index = None
            st.rerun()
        
        # Event details
        st.markdown(f"### {event['city']}, {event['state']}")
        st.markdown(f"**Event:** {event['event']}")
        st.markdown(f"**Date:** {event['date-of-event'].strftime('%B %d, %Y')}")
        
        if pd.notna(event['summary']):
            st.markdown("**Summary:**")
            st.markdown(event['summary'])
        
        if pd.notna(event['event-picture-link']):
            try:
                st.image(
                    event['event-picture-link'],
                    caption=event['event-picture-caption'] if pd.notna(event['event-picture-caption']) else None,
                    use_column_width=True
                )
            except Exception:
                st.error("Unable to load image")

# Optional: Display data table
with st.expander("View All Events"):
    st.dataframe(
        filtered_events_df[[
            'city', 'state', 'event', 'date-of-event', 'summary'
        ]].sort_values('date-of-event', ascending=False),
        use_container_width=True
    )
