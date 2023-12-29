import streamlit as st
import pandas as pd
import os
import shutil
from pages import home_page as home


def main():
    """
    A self contained page of streamlit app. It gives option to upload the data. 
    it Reads the data and passes it as dataframe to `/page/components/home.py`
    """
    st.set_page_config(layout="wide")  # Set layout to wide
    st.markdown("---")

    # read the csv file.
    df = pd.read_csv('simplemaps_worldcities_basicv1.76\worldcities.csv', 
    usecols = ['city', 'lat', 'lng','iso3', 'population', 'capital', 'admin_name', 'country'])
    # pass the dataframe to home_page function in home.py
    home.home_page(df)


if __name__ == "__main__":
    main()
