import time

import streamlit as st
import numpy as np
import pandas as pd
from bokeh.layouts import row

from data import load_data_trips_duration, load_data_trips_income, load_data_trips_length, load_data_trips_purpose, load_zones, get_trip_ends, get_cds
from data import CHOICES_DAY_TYPE, CHOICES_DAY_PART, INDEX_PURPOSE, INDEX_DURATION, INDEX_INCOME, INDEX_LENGTH
from plot import plot_trips, plot_zones

def main():

    st.title('Trip Insights Viz')
    st.markdown('''
        This app shows insights into trips made in a city in Virginia. The data source is Streetlight Data,   
        which uses location-based services and GPS data.
    
    ''')
    
    # Load the data
    with st.spinner('Loading Data...'):
        df_trips_purpose = load_data_trips_purpose()
        df_trips_duration = load_data_trips_duration()
        df_trips_length = load_data_trips_length()
        df_trips_income = load_data_trips_income()
    st.success("Data Loaded Successfully")

    min_zone = int(min(df_trips_purpose['Origin Zone ID'].min(), df_trips_purpose['Destination Zone ID'].min()))
    max_zone = int(max(df_trips_purpose['Origin Zone ID'].max(), df_trips_purpose['Destination Zone ID'].max()))
    
    # Compose the widgets
    choice_day_type = st.sidebar.selectbox("Please select the type of a day", list(CHOICES_DAY_TYPE.keys()))
    choice_day_part = st.sidebar.multiselect("Please select the period of a day", list(CHOICES_DAY_PART.keys()), default=("All Day (12am-12am)",))
    choice_origin_lb = st.sidebar.slider('Select the lower bound for origins', min_value=min_zone, max_value=max_zone)
    choice_origin_ub = st.sidebar.slider('Select the upper bound for origins', min_value=min_zone, max_value=max_zone, value=max_zone)
    choice_destination_lb = st.sidebar.slider('Select the lower bound for destinations', min_value=min_zone, max_value=max_zone)
    choice_destination_ub = st.sidebar.slider('Select the upper bound for destinations', min_value=min_zone, max_value=max_zone, value=max_zone)
    
    origin = (choice_origin_lb, choice_origin_ub)
    destination = (choice_destination_lb, choice_destination_ub)
    origin_count = choice_origin_ub - choice_origin_lb + 1
    dest_count = choice_destination_ub - choice_destination_lb + 1

    if "All Day (12am-12am)" in choice_day_part:
        choice_day_part = ("All Day (12am-12am)", )

    # Acknowledge the choices
    st.markdown(
        '''
            #### Selection Criteria  
            * Day: __{0}__
            * Period: __{1}__
            * Origin Zones: __{2:d} ~ {3:d}__ 
            * Destination Zones: __{4:d} ~ {5:d}__
        '''.format(choice_day_type, choice_day_part, choice_origin_lb, choice_origin_ub, choice_destination_lb, choice_destination_ub)
    )

    # Make Plots
    trips_origin, trips_dest = get_trip_ends(
        df_trips_purpose, 
    origin=origin, destination=destination, 
    day_type=choice_day_type, day_part=choice_day_part
    )
    zones = load_zones()

    cds_purpose = get_cds(df_trips_purpose, INDEX_PURPOSE, "Purpose", origin, destination, choice_day_type, choice_day_part)
    cds_duration = get_cds(df_trips_duration, INDEX_DURATION, "Duration", origin, destination, choice_day_type, choice_day_part)
    cds_income = get_cds(df_trips_income, INDEX_INCOME, "Income", origin, destination, choice_day_type, choice_day_part)
    cds_length = get_cds(df_trips_length, INDEX_LENGTH, "Length", origin, destination, choice_day_type, choice_day_part)

    p_purpose = plot_trips(cds_purpose, "Purpose", color='blue')
    p_duration = plot_trips(cds_duration, "Duration", color='firebrick')
    p_income = plot_trips(cds_income, "Income", color='lime')
    p_length = plot_trips(cds_length, "Length", color='orange')

    p_zone = plot_zones(zones, trips_origin)

    total_trips = int(cds_purpose.to_df().Trips.sum())

    st.markdown('''

        #### Analyis Results
        
        Total number of trips: __{:,d}__  
        Total number of origins: __{:,d}__  
        Total number of destinations: __{:,d}__  
    '''.format(total_trips, origin_count, dest_count))

    st.markdown(
        '''
    ### Who and Why are they making the trips?
    Distributions of Trip Purpose and Income
    '''
    )
    l1 = row(p_purpose, p_income)
    st.bokeh_chart(l1)

    st.markdown(
        '''
    ### How far and How long are the trips?
    Distributions of Trip Length and Distribution
    '''
    )
    l2 = row(p_length, p_duration)
    st.bokeh_chart(l2)

    st.markdown(
        '''
    ### Where do the trips originate?
    Trip Origins
    '''
    )
    st.bokeh_chart(p_zone)

if __name__ == '__main__':
    main()

    