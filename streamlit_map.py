import streamlit as st
import pandas as pd
import numpy as np
import supabase

#Connect to supabase




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
