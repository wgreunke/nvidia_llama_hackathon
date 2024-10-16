import streamlit as st
import pandas as pd
import numpy as np
import supabase

#Connect to supabase

s_url=st.secrets["supabase_url"]
s_key=st.secrets["supabase_key"]
st.write(s_url)

#st.write("DB username:", st.secrets["db_username"])

supabase = supabase.create_client(s_url, s_key)
#get the events table and print out the results
event_results = supabase.table("events").select("*").execute()
st.write(event_results.data)





data = {
    'event_date':[10,30,20],
    'City': ['Tampa, FL', 'Banner Elk, NC', 'Orlando'],
    'lat': [27.964157, 36.1631800, 30.2111],
    'lon': [-82.452606, -81.8715000, - 82.4911]
}

event_data=pd.DataFrame(data)
 
#Add the slider
selected_date_range = st.slider("Select a date range",0,50, step=5)

filtered_df = event_data[event_data['event_date'] <= selected_date_range]

st.map(filtered_df,size=200,color="#0044ff")

st.write(filtered_df)
