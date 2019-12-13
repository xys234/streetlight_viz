import os
from typing import Tuple
from math import pi

import numpy as np
import pandas as pd
import geopandas as gpd
import streamlit as st

from bokeh.models import ColumnDataSource


DATA_FOLDER = r"../data"
OD_TRIP_FILE_PURPOSE = os.path.join(DATA_FOLDER, r"od_trip_purpose_counts.csv.gz")
OD_TRIP_FILE_DEMOGRAPHICS = os.path.join(DATA_FOLDER, r"od_demographics_counts.csv.gz")
OD_TRIP_FILE_ATTRIBUTES = os.path.join(DATA_FOLDER, r"od_trip_attributes_counts_all.csv.gz")
ZONE_SHAPE_FILE = os.path.join(DATA_FOLDER, '../data/zone.shp')


INDEX_COLUMNS = ["Origin Zone ID", "Destination Zone ID", "Day Type", "Day Part"]


CHOICES_DAY_TYPE = {
    "Average Day (M-Su)":"0: Average Day (M-Su)",
    "Average Weekday (M-F)":"1: Average Weekday (M-F)",
    "Average Weekend Day (Sa-Su)":"2: Average Weekend Day (Sa-Su)"
}

CHOICES_DAY_PART = {
    "All Day (12am-12am)": "0: All Day (12am-12am)",
    "Early AM (12am-6am)": "1: Early AM (12am-6am)",
    "Peak AM (6am-10am)": "2: Peak AM (6am-10am)",
    "Mid-Day (10am-3pm)": "3: Mid-Day (10am-3pm)",
    "Peak PM (3pm-7pm)": "4: Peak PM (3pm-7pm)",
    "Late PM (7pm-12am)": "5: Late PM (7pm-12am)",
}

TRIP_PURPOSES = {
    "HBW": "Purpose HBW (percent)",
    "HBO": "Purpose HBO (percent)",
    "NHB": "Purpose NHB (percent)"
}

TRIP_COUNT_TYPES = {
    "STL": "O-D Traffic (StL Index)",
}

TRIP_DURATION_BINS = {
    "0-10 min" : "Trip Duration 0-10 min (percent)",       
    "10-20 min": "Trip Duration 10-20 min (percent)",      
    "20-30 min": "Trip Duration 20-30 min (percent)",      
    "30-40 min": "Trip Duration 30-40 min (percent)",      
    "40-50 min": "Trip Duration 40-50 min (percent)",      
    "50-60 min": "Trip Duration 50-60 min (percent)",      
    "60-70 min": "Trip Duration 60-70 min (percent)",      
    "70-80 min": "Trip Duration 70-80 min (percent)",      
    "80-90 min": "Trip Duration 80-90 min (percent)",      
    "90-100 min":  "Trip Duration 90-100 min (percent)",     
    "100-110 min": "Trip Duration 100-110 min (percent)",    
    "110-120 min": "Trip Duration 110-120 min (percent)",    
    "120-130 min": "Trip Duration 120-130 min (percent)",    
    "130-140 min": "Trip Duration 130-140 min (percent)",    
    "140-150 min": "Trip Duration 140-150 min (percent)",    
    "150+ min":  "Trip Duration 150+ min (percent)"    
}

TRIP_LENGTH_BINS = {
    
    "0-1 mi":    "Trip Length 0-1 mi (percent)",           
    "1-2 mi":    "Trip Length 1-2 mi (percent)",           
    "2-5 mi":    "Trip Length 2-5 mi (percent)",           
    "5-10 mi":   "Trip Length 5-10 mi (percent)",          
    "10-20 mi":  "Trip Length 10-20 mi (percent)",         
    "20-30 mi":  "Trip Length 20-30 mi (percent)",         
    "30-40 mi":  "Trip Length 30-40 mi (percent)",         
    "40-50 mi":  "Trip Length 40-50 mi (percent)",         
    "50-60 mi":  "Trip Length 50-60 mi (percent)",         
    "60-70 mi":  "Trip Length 60-70 mi (percent)",         
    "70-80 mi":  "Trip Length 70-80 mi (percent)",         
    "80-90 mi":  "Trip Length 80-90 mi (percent)",         
    "90-100 mi": "Trip Length 90-100 mi (percent)",        
    "100+ mi":   "Trip Length 100+ mi (percent)"         
    
}

INCOME_BINS = {
    "<20K":         "Income Less than 20K (percent)",            
    "20K to 35K":   "Income 20K to 35K (percent)",               
    "35K to 50K":   "Income 35K to 50K (percent)",               
    "50K to 75K":   "Income 50K to 75K (percent)",               
    "75K to 100K":  "Income 75K to 100K (percent)",              
    "100K to 125K": "Income 100K to 125K (percent)",             
    "125K to 150K": "Income 125K to 150K (percent)",             
    "150K to 200K": "Income 150K to 200K (percent)",             
    "200K+":        "Income More than 200K (percent)"  
}

SHARED_COLUMNS = INDEX_COLUMNS + list(TRIP_COUNT_TYPES.values())

COLUMNS_TRIP_PURPOSE = SHARED_COLUMNS + list(TRIP_PURPOSES.values())
COLUMNS_TRIP_INCOME = SHARED_COLUMNS + list(INCOME_BINS.values())
COLUMNS_TRIP_DURATION = SHARED_COLUMNS + list(TRIP_DURATION_BINS.values())
COLUMNS_TRIP_LENGTH = SHARED_COLUMNS + list(TRIP_LENGTH_BINS.values())

INDEX_PURPOSE = pd.Index(list(TRIP_PURPOSES.values()), name="Purpose")
INDEX_INCOME = pd.Index(list(INCOME_BINS.values()), name="Income")
INDEX_DURATION = pd.Index(list(TRIP_DURATION_BINS.values()), name="Duration")
INDEX_LENGTH = pd.Index(list(TRIP_LENGTH_BINS.values()), name="Length")


def transform(df, dimensions, dimension_name):
    
    # Compute the trips
    for d in dimensions:
        df[d] = df[TRIP_COUNT_TYPES["STL"]] * df[d]
    df = pd.melt(df, id_vars=INDEX_COLUMNS, value_vars=dimensions, var_name=dimension_name, value_name="Trips")
    
    return df

@st.cache
def load_data_trips_purpose() -> pd.DataFrame:
    df_trips_purpose = pd.read_csv(OD_TRIP_FILE_PURPOSE, na_values="N/A").fillna(0)
    df_trips_purpose = transform(df_trips_purpose, list(TRIP_PURPOSES.values()), "Purpose")
    return df_trips_purpose

@st.cache
def load_data_trips_income() -> pd.DataFrame:
    df_trips_income = pd.read_csv(OD_TRIP_FILE_DEMOGRAPHICS, na_values="N/A").loc[:, COLUMNS_TRIP_INCOME].fillna(0)
    df_trips_income = transform(df_trips_income, list(INCOME_BINS.values()), "Income")
    return df_trips_income

@st.cache
def load_data_trips_duration() -> pd.DataFrame:
    df_trips_duration = pd.read_csv(OD_TRIP_FILE_ATTRIBUTES, na_values="N/A").loc[:, COLUMNS_TRIP_DURATION].fillna(0)
    df_trips_duration = transform(df_trips_duration, list(TRIP_DURATION_BINS.values()), "Duration")
    return df_trips_duration

@st.cache
def load_data_trips_length() -> pd.DataFrame:
    df_trips_length = pd.read_csv(OD_TRIP_FILE_ATTRIBUTES, na_values="N/A").loc[:, COLUMNS_TRIP_LENGTH].fillna(0)
    df_trips_length = transform(df_trips_length, list(TRIP_LENGTH_BINS.values()), "Length")
    return df_trips_length

@st.cache
def load_zones() -> gpd.GeoDataFrame:
    zone = gpd.read_file(ZONE_SHAPE_FILE).to_crs({'init': 'epsg:3857'})
    return zone

def get_cds(df, index, attr, origin = (1, 166), destination = (1, 166), day_type = "Average Day (M-Su)", day_part = ("All Day (12am-12am)",)):
    selector_origin = (df["Origin Zone ID"] >= origin[0]) & (df["Origin Zone ID"] <= origin[1])
    selector_destination = (df["Destination Zone ID"] >= destination[0]) & (df["Destination Zone ID"] <= destination[1])
    selector_day_type = df['Day Type'] == CHOICES_DAY_TYPE[day_type]
    selector_day_part = df['Day Part'].isin([CHOICES_DAY_PART[d] for d in day_part])
    
    df_filtered = df.loc[selector_origin&selector_destination&selector_day_type&selector_day_part, df.columns]
    df_filtered = df_filtered.groupby(attr)['Trips'].sum().reindex(index).fillna(0).reset_index()
    df_filtered['Trips'] = df_filtered.Trips.astype(int)
    
    # Remove percent
    df_filtered[attr] = df_filtered[attr].apply(lambda x: x[:(len(x)-len("(percent)")-1)]) 
    
    cds = ColumnDataSource(data=df_filtered)
    return cds

def get_trip_ends(df: pd.DataFrame, origin = (1, 166), destination = (1, 166), day_type = "Average Day (M-Su)", day_part = ("All Day (12am-12am)",)):
    selector_origin = (df["Origin Zone ID"] >= origin[0]) & (df["Origin Zone ID"] <= origin[1])
    selector_destination = (df["Destination Zone ID"] >= destination[0]) & (df["Destination Zone ID"] <= destination[1])
    selector_day_type = df['Day Type'] == CHOICES_DAY_TYPE[day_type]
    selector_day_part = df['Day Part'].isin([CHOICES_DAY_PART[d] for d in day_part])
    
    df_filtered = df.loc[selector_origin&selector_destination&selector_day_type&selector_day_part, df.columns]
    
    trips_origin = df_filtered.groupby("Origin Zone ID", as_index=False)['Trips'].sum()
    trips_dest = df_filtered.groupby("Destination Zone ID", as_index=False)['Trips'].sum()
    
    trips_origin['Trips'] = trips_origin['Trips'].astype(int)
    trips_dest['Trips'] = trips_dest['Trips'].astype(int)
    
    return trips_origin, trips_dest




