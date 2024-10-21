import streamlit as st
import pandas as pd
import numpy as np
import supabase
import os

#Streamlit url
#https://newsmap.streamlit.app/


# ----------------Load the events.csv file --------------------------------
csv_file_name="events.csv"
path=""
events_df = pd.read_csv(os.path.join(path,csv_file_name))

#Convert the column date-of-event to a python date that can be filterd
events_df['date-of-event'] = pd.to_datetime(events_df['date-of-event'])
st.write(events_df)


selected_date = st.slider(
    'Select a date to filter events before this date',
    min_value=events_df['date-of-event'].min(),
    max_value=events_df['date-of-event'].max(),
    value=events_df['date-of-event'].max(),
    format="YYYY-MM-DD"
)



filtered_events_df = events_df[events_df['date-of-event'] <= selected_date]
st.write(filtered_events_df)


#Add the slider
data = {
    'event_date':[10,30,20],
    'City': ['Tampa, FL', 'Banner Elk, NC', 'Orlando'],
    'lat': [27.964157, 36.1631800, 30.2111],
    'lon': [-82.452606, -81.8715000, - 82.4911]
}

event_data=pd.DataFrame(data)


selected_date_range = st.slider("Select a date range",0,50, step=5)

filtered_df = event_data[event_data['event_date'] <= selected_date_range]

st.map(filtered_df,size=200,color="#0044ff")

st.write(filtered_df)
