import pandas as pd
import warnings
from datetime import datetime
import plotly.express as px
pd.set_option('display.max_columns', None)
warnings.filterwarnings('ignore')
import streamlit as st
import plotly.express as px 
import requests
import plotly as plt


#Title & page config
st.set_page_config(
    page_icon= ":bar_chart:",
    layout= "wide")
st.title('S&P/Case-Shiller Home Price Index')


#S&P/Case-Shiller AZ-Phoenix Home Price Index (PHXRNSA)
fred_api= 'b8830a9164d01e4df457386e8e500095'
series_id = 'PHXRNSA'
params = {
    'series_id': series_id,
    'api_key': fred_api,
    'file_type': 'json'
            }

response = requests.get('https://api.stlouisfed.org/fred/series/observations', params=params)

# Check the response status code to make sure the request was successful
if response.status_code == 200:
    data = response.json()
    # Process the data as needed...
else:
    print('Failed to download data:', response.text)

# Parse the response from the FRED API into a Pandas DataFrame
df = pd.DataFrame(response.json()["observations"])
df = df[['date','value']]
df = (df.assign(
                value = df['value'].astype('float').round(2),
                date = pd.to_datetime(df['date']).dt.date,
                mom_value = round((df['value'].astype('float').round(2).pct_change())*100,2),
                yoy_value = round((df['value'].astype('float').round(2).pct_change(12))*100,2)
))
df['mom_latest'] = df['mom_value'].iloc[-1]
df['yoy_latest'] = df['yoy_value'].iloc[-1]

latest_value = df['value'].iloc[-1]
mom_latest = df['mom_value'].iloc[-1]
yoy_latest = df['yoy_value'].iloc[-1]


# Calculate the MOM and YOY changes for the latest value
latest_value = df['value'].iloc[-1]
previous_value = df['value'].iloc[-2]
mom_latest = df['mom_value'].iloc[-1]
mom_previous = df['mom_value'].iloc[-2]
yoy_latest = df['yoy_value'].iloc[-1]
yoy_previous = df['yoy_value'].iloc[-2]
last_month_name = df['date'].iloc[-1]

# Create a new Pandas DataFrame with the data
data = {'Related': ['Case Shiller Home Price Index MoM', 'Case Shiller Home Price Index YoY','Case Shiller Price Index'],
        'Last': [mom_latest, yoy_latest,latest_value],
        'Previous': [mom_previous, yoy_previous,previous_value],
        'Unit': ['percent', 'percent','points'],
        'Reference': [last_month_name, last_month_name,last_month_name]}
calculations_df = pd.DataFrame(data)

# Display the table in Streamlit
st.write("The Case-Shiller Home Price Index is a tool used to track changes in home values in the U.S. It is based on data from the S&P CoreLogic Case-Shiller Home Price Indices, which cover 20 metropolitan areas.")

st.write("- The Index is published monthly and is based on a 3-month moving average of home prices.")
st.write("- It is presented in index form, with the value of 100 representing the average home price in January 2000.")
st.write("- For example, if the Case-Shiller Index for a particular area is 150, it means that home prices in that area are 50% higher than in January 2000.")

st.subheader('Phoenix Index - FRED API')
st.dataframe(calculations_df)
st.write('Case-Shiller Index for Phoenix, Arizona')
st.bar_chart(df,x = 'date',y = 'value',width=3)

st.write("This index is used by economists, real estate professionals, and financial analysts to gauge the health of the housing market. It is also used by policymakers to make decisions about monetary policy and the economy.")

st.write("Overall, the Case-Shiller Home Price Index is a valuable tool for understanding trends in the housing market and the health of the economy. It is a key indicator of the strength of the housing market and can provide insight into the direction of the economy as a whole.")