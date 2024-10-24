import streamlit as st
import pandas as pd
import numpy as np
import supabase
import os
import datetime

#Streamlit url
#https://newsmap.streamlit.app/


# ----------------Load the events.csv file --------------------------------
csv_file_name="events.csv"
path=""
events_df = pd.read_csv(os.path.join(path,csv_file_name))

#Convert the column date-of-event to a python date that can be filterd
events_df['date-of-event'] = pd.to_datetime(events_df['date-of-event'])

st.write(events_df)

min_date = events_df['date-of-event'].min().to_pydatetime().date()
max_date = events_df['date-of-event'].max().to_pydatetime().date()
initial_date = events_df['date-of-event'].min().to_pydatetime().date()
# Check if min_date and max_date are the same
# If they are the same, add one day to max_date to create a range for the slider.
if min_date == max_date:
    max_date = max_date + datetime.timedelta(days=5)  # Add one day to max_date


# Create slider with correct date range (fixed)
selected_date = st.slider(
    'Select a date to filter events before this date',
    min_value=min_date,
    max_value=max_date,
    value=initial_date,
    format="YYYY-MM-DD"
)

#Convert to python date
selected_date=pd.Timestamp(selected_date)
filtered_events_df = events_df[events_df['date-of-event'] <= selected_date]
#st.write(filtered_events_df)


#Add the slider
data = {
    'event_date':[10,30,20],
    'City': ['Tampa, FL', 'Banner Elk, NC', 'Orlando'],
    'lat': [27.964157, 36.1631800, 30.2111],
    'lon': [-82.452606, -81.8715000, - 82.4911]
}

event_data=pd.DataFrame(data)


#selected_date_range = st.slider("Select a date range",0,50, step=5)

#filtered_df = event_data[event_data['event_date'] <= selected_date_range]

st.map(filtered_events_df,size=200,color="#0044ff")

st.write(filtered_events_df)
