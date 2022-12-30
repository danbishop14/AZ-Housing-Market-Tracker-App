import streamlit as st
import pandas as pd
from datetime import datetime
import warnings
import plotly.express as px
pd.set_option('display.max_columns', None)
warnings.filterwarnings('ignore')
import pandas_datareader.data as web
import plotly as plt


#Full Data Caching
url = "https://redfin-public-data.s3.us-west-2.amazonaws.com/redfin_market_tracker/zip_code_market_tracker.tsv000.gz"
@st.experimental_memo
def get_data() -> pd.DataFrame:
    return pd.read_csv(url, compression='gzip', sep='\t')
df = get_data()

def get_az_data() -> pd.DataFrame:
    mapping_df = pd.read_csv('https://raw.githubusercontent.com/scpike/us-state-county-zip/master/geo-data.csv')
    mapping_df  = (mapping_df.assign(zipcode = mapping_df['zipcode'].loc[mapping_df['zipcode'].str.isnumeric()].astype(int)).drop(columns=['state_fips']).dropna())
    az_df = (df.loc[df['state_code'] == 'AZ'].assign(period_end = pd.to_datetime(df['period_end']),zipcode = df['region'].str.replace('Zip Code:','').astype(int)).merge(mapping_df, on = 'zipcode', how = 'inner').drop(columns = ['region','city_x','state_x']).rename(columns = {'city_y':'city','state_y':'state'}))
    cities_we_want = ["Phoenix", "Tuscon", "Mesa", "Chandler", "Scottsdale", "Paradise valley","Flagstaff","Tempe","Gilbert","Goodyear","Yuma","Prescott","Sedona","Cave creek"]
    az_df = az_df[az_df.city.isin(cities_we_want)]
    return az_df
az_df = get_az_data()

city = st.columns([5])
cities_we_want = ["Phoenix", "Mesa", "Chandler", "Scottsdale", "Paradise valley","Flagstaff","Tempe","Gilbert","Goodyear","Buckeye","Yuma","Prescott","Sedona","Cave creek"]


with st.sidebar:
    st.markdown("# Filter")
    city_choice = st.selectbox(
         "***Choose City***",
        ('All',"Phoenix", "Mesa", "Chandler", "Scottsdale", "Paradise valley","Flagstaff","Tempe","Gilbert","Goodyear","Yuma","Prescott","Sedona","Cave Creek")
    )



 #Filter Interactions
if city_choice == 'All':
    filtered_df = az_df
else:
    filtered_df = az_df[az_df['city'] == city_choice]


#Pulling the latest Median Sale Price for each city + property type
filtered_df = filtered_df[~filtered_df['property_type'].isin(['Multi-Family (2-4 Unit)', 'All Residential','Condo/Co-op','Townhouse'])]
filtered_df = filtered_df.assign(year = filtered_df['period_end'].dt.year,month = filtered_df['period_end'].dt.month,short_month_name = filtered_df['period_end'].dt.strftime('%b')
                   )

#Define a function to generate the dataframe
@st.cache
def get_filtered_df():
    df = pd.DataFrame(filtered_df)
    return df

# On the first page, retrieve the dataframe and display it
df12 = get_filtered_df()


msp = pd.DataFrame(filtered_df.groupby(['city','period_end'])['median_sale_price','median_sale_price_mom','median_sale_price_yoy'].mean()).reset_index()

#Define a function to generate the dataframe
@st.cache
def get_msp_df():
    df = pd.DataFrame(msp)
    return df
df13 = get_msp_df()

homes_sold = pd.DataFrame(filtered_df.groupby(['city','period_end'])['homes_sold'].sum()).reset_index()
homes_sold = (homes_sold.assign(
                            homes_sold_mom = homes_sold['homes_sold'].pct_change(),
                            homes_sold_yoy = homes_sold['homes_sold'].pct_change(periods=12)))
latest_msp = msp.loc[msp.groupby(['city'])['period_end'].idxmax()]

#Homes sold in the last month
homes_sold_int = homes_sold.sort_values('period_end',ascending = True)
homes_sold_number = homes_sold_int['homes_sold'].iloc[-1]
homes_sold_mom_number = homes_sold_int['homes_sold_mom'].iloc[-1]
homes_sold_yoy_number = homes_sold_int['homes_sold_yoy'].iloc[-1]
latest_hs = homes_sold.loc[homes_sold.groupby(['city','period_end'])['period_end'].idxmax()]
latest_msp = latest_msp[latest_msp['city'].isin(cities_we_want)]
latest_hs = latest_hs[latest_hs['city'].isin(cities_we_want)]


#METRICS
#median sale price, homes sold, national avg 30 year fixed mortgage rate
med_sp =  "${:,.2f}".format(latest_msp['median_sale_price'].median())
med_sp_mom = "{:.1%}".format((latest_msp['median_sale_price_mom'].median()))
med_sp_yoy = "{:.1%}".format((latest_msp['median_sale_price_yoy'].median()))

#unformatted med sp mom
msp_mom_value = latest_msp['median_sale_price_mom'].median()

# calculate the sum of the "homes_sold" column
total = latest_hs['homes_sold'].sum()

# round the total to the nearest integer
rounded_total = round(total, 0)

# convert the rounded total to an integer
int_total = int(rounded_total)

# format the integer as a string with a comma as a thousands separator
formatted_total = "{:,}".format(homes_sold_number)
#current_hs_count = "{:,}" .format(str(int(round(latest_hs['homes_sold'].sum(),0))))
current_hs_mom = "{:.1%}".format(homes_sold_mom_number)
current_hs_mom2 = latest_hs['homes_sold_mom'].mean()
current_hs_yoy = str(latest_hs['homes_sold_yoy'].mean())
current_hs_yoy2 = homes_sold_yoy_number

#Pulling mortgage data from the FRED API.
#Collecting the 30 year fixed rate from FRED
api_key = '#################################'
data = web.DataReader("MORTGAGE30US", "fred", api_key=api_key)
# print the latest value
latest_mortgage_rate = data["MORTGAGE30US"].iloc[-1]
last_years_rate = data['MORTGAGE30US'].iloc[-52]
yoy_diff = latest_mortgage_rate-last_years_rate
# print the last week name
mort_data = data.reset_index()
mort_data = (mort_data
                        .assign(
                            DATE = mort_data['DATE'],
                            month = mort_data['DATE'].dt.month,
                            day = mort_data['DATE'].dt.day
                        ))
month_mort = mort_data.iloc[-1]['month']
day_mort = mort_data.iloc[-1]['day']

def month_name(latest_month):
    # Create a dictionary that maps month numbers to month names
    month_names = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December"
    }
    month_name = month_names.get(latest_month)
    return month_name

latest_month = latest_msp['period_end'].dt.month.iloc[0]

#Caching latest month for page header
@st.cache
def latest_month_value():
    return month_name(latest_month)

previous_month_name = latest_month-1

# returns seleceted city name
def get_city(city_choice):
    # Use the if statement to evaluate the city_choice argument
    if city_choice == "All":
        # If city_choice is "All", write "all cities" to the screen
        return "all cities"
    else:
        # If city_choice is not "All", write the city_choice to the screen
        return city_choice

def inc_or_dec(percent_change):
    if percent_change > 0:
        return str(round(percent_change*100,1)) + '\% increase'
    else:
        return str(round(percent_change*100,1)) + "\% decrease"

def up_or_down_mom(percent_change):
    if percent_change > 0:
        return "up " +str(round(percent_change*100,1))+ "%"
    else:
        return "down " +str(round(percent_change*100,1))+ "%"       


def add_suffix(number):
    # Convert the number to a string
    number_str = str(number)

    # Get the last digit of the number
    last_digit = int(number_str[-1])

    # Add the appropriate suffix
    if last_digit == 1:
        return number_str + "st"
    elif last_digit == 2:
        return number_str + "nd"
    elif last_digit == 3:
        return number_str + "rd"
    else:
        return number_str + "th"



# st.dataframe(get_cool_pivot(msp))
def get_cool_pivot(df):
    from datetime import datetime

    # Group the data by property_type and period_end, and calculate the median median_sale_price
    grouped_df = df.groupby(['property_type','period_end'])['median_sale_price'].mean().reset_index()

    # Pivot the grouped data to create the dataframe with the last two months as columns
    pivoted_df = grouped_df.pivot_table(index=['property_type'], columns=['period_end'], values=['median_sale_price'])

    # Extract the datetime objects from the pivoted_df.columns object
    last_month = pivoted_df.columns[-1][1]
    second_to_last_month = pivoted_df.columns[-2][1]

    # Get the names of the last two months
    last_month_name = datetime.strftime(last_month, "%B")
    second_to_last_month_name = datetime.strftime(second_to_last_month, "%B")

    # Rename the columns to the names of the last two months
    pivoted_df = pivoted_df.rename(columns={
        last_month: last_month_name,
        second_to_last_month: second_to_last_month_name})

    # Select only the last two columns from the pivoted_df dataframe
    pivoted_df = pivoted_df.iloc[:,-2:]

    # Calculate the percentage change between the last two columns
    pivoted_df['pct_Change'] = round(((pivoted_df.iloc[:,1] - pivoted_df.iloc[:,0]) / pivoted_df.iloc[:,0])*100,2)

    # Remove the rows of columns
    pivoted_df.columns = pivoted_df.columns.droplevel(0)
    pivoted_df = pivoted_df.rename(columns = {"":"% Change"})

    return pivoted_df


def zip_msp(df):
    from datetime import datetime

    # Group the data by city and zipcode, and calculate the median median_sale_price
    grouped_df = df.groupby(['city','zipcode','period_end'])['median_sale_price'].mean().reset_index()

    # Pivot the grouped data to create the dataframe with the last two months as columns
    pivoted_df = grouped_df.pivot_table(index=['city','zipcode'], columns=['period_end'], values=['median_sale_price'])

    # Extract the datetime objects from the pivoted_df.columns object
    last_month = pivoted_df.columns[-1][1]
    second_to_last_month = pivoted_df.columns[-2][1]

    # Get the names of the last two months
    last_month_name = datetime.strftime(last_month, "%B")
    second_to_last_month_name = datetime.strftime(second_to_last_month, "%B")

    # Rename the columns to the names of the last two months
    pivoted_df.columns = pivoted_df.columns.droplevel(0)
    pivoted_df = pivoted_df.rename(columns={
        last_month: last_month_name,
        second_to_last_month: second_to_last_month_name
    })

    # Select only the last two columns from the pivoted_df dataframe
    pivoted_df = pivoted_df.iloc[:,-2:]

    # Calculate the percentage change between the last two columns
    pivoted_df['%\ Change'] = round(((pivoted_df.iloc[:,1] - pivoted_df.iloc[:,0]) / pivoted_df.iloc[:,0])*100,2)

    # Sort the DataFrame by the '%\ Change' column in descending order
    pivoted_df = pivoted_df.rename(columns={'%\ Change': '% Change'}).sort_values(by='% Change', ascending=False)

    return pivoted_df
    #

#Creating new table for mom median sales price by city
def city_msp(df):
    from datetime import datetime

    # Group the data by city and zipcode, and calculate the median median_sale_price
    grouped_df = df.groupby(['city','period_end'])['median_sale_price'].mean().reset_index()

    # Pivot the grouped data to create the dataframe with the last two months as columns
    pivoted_df = grouped_df.pivot_table(index=['city'], columns=['period_end'], values=['median_sale_price'])

    # Extract the datetime objects from the pivoted_df.columns object
    last_month = pivoted_df.columns[-1][1]
    second_to_last_month = pivoted_df.columns[-2][1]

    # Get the names of the last two months
    last_month_name = datetime.strftime(last_month, "%B")
    second_to_last_month_name = datetime.strftime(second_to_last_month, "%B")

    # Rename the columns to the names of the last two months
    pivoted_df.columns = pivoted_df.columns.droplevel(0)
    pivoted_df = pivoted_df.rename(columns={
        last_month: last_month_name,
        second_to_last_month: second_to_last_month_name
    })

    # Select only the last two columns from the pivoted_df dataframe
    pivoted_df = pivoted_df.iloc[:,-2:]

    # Calculate the percentage change between the last two columns
    pivoted_df['%\ Change'] = round(((pivoted_df.iloc[:,1] - pivoted_df.iloc[:,0]) / pivoted_df.iloc[:,0])*100,2)

    # Sort the DataFrame by the '%\ Change' column in descending order
    pivoted_df = pivoted_df.rename(columns={'%\ Change': '% Change'}).sort_values(by='% Change', ascending=False)
    
    return pivoted_df
    #

def homes_sold(df):
    from datetime import datetime
    df = df.groupby(['city','period_end'])['homes_sold'].sum().reset_index()
    
    # Pivot the grouped data to create the dataframe with the last two months as columns
    pivoted_df = df.pivot_table(index=['city'], columns=['period_end'], values=['homes_sold'])

    # Extract the datetime objects from the pivoted_df.columns object
    last_month = pivoted_df.columns[-1][1]
    second_to_last_month = pivoted_df.columns[-2][1]

    # Get the names of the last two months
    last_month_name = datetime.strftime(last_month, "%B")
    second_to_last_month_name = datetime.strftime(second_to_last_month, "%B")

    # Rename the columns to the names of the last two months
    pivoted_df.columns = pivoted_df.columns.droplevel(0)
    pivoted_df = pivoted_df.rename(columns={
        last_month: last_month_name,
        second_to_last_month: second_to_last_month_name
    })

    # Select only the last two columns from the pivoted_df dataframe
    pivoted_df = pivoted_df.iloc[:,-2:]

    # Calculate the percentage change between the last two columns
    pivoted_df['%\ Change'] = round(((pivoted_df.iloc[:,1] - pivoted_df.iloc[:,0]) / pivoted_df.iloc[:,0])*100,2)

    # Sort the DataFrame by the '%\ Change' column in descending order
    pivoted_df = pivoted_df.rename(columns={'%\ Change': '% Change'}).sort_values(by='% Change', ascending=False)
    
    return pivoted_df

#Title
st.title('Arizona Housing Market Snapshot')

text = 'As of ' + str(month_name(latest_month)) + ', 2022'
#Showing results as:
st.write(text)

#Short text writeup
st.markdown(
"""
- Single family home prices saw a %s from %s.
- %s homes were sold in %s, a %s from last year and %s month-over-month.
- The 30-year fixed mortgage rate is currently %s as of %s according to Federal Reserve Economic Data (FRED).
"""
% (inc_or_dec(msp_mom_value), month_name(previous_month_name),homes_sold_number,get_city(city_choice), inc_or_dec(current_hs_yoy2),up_or_down_mom(homes_sold_mom_number),round(latest_mortgage_rate,2),str(month_name(month_mort)) +", " +str(add_suffix(day_mort)))
)
st.markdown("<hr>", unsafe_allow_html=True)


#Large KPIs
m1,m2,m3 = st.columns(3)
with m1:
    m1.metric('Median Sale Price', (med_sp), delta = str(med_sp_mom) + " month-over-month")
    
with m2:
    m2.metric("\# of Homes Sold", formatted_total, delta = str(current_hs_mom) + " month-over-month")

with m3:
   m3.metric('Avg. 30-Year Fixed Mortgage Rate', latest_mortgage_rate, delta = str(round(yoy_diff, 2)) + " pts year-over-year",delta_color='inverse')

st.markdown("<hr>", unsafe_allow_html=True)

# Add a new section to the dashboard
st.subheader("Last Month's Changes")

m1, m2 = st.columns([2,8])
with m1:
    dataframe_selection = st.radio("Select a view:", ("City Prices", "Zip Code Prices", "Homes Sold"))
with m2:
    # Display the selected dataframe as a table
    if dataframe_selection == "Homes Sold":
        st.dataframe(homes_sold(filtered_df))
    elif dataframe_selection == "City Prices":
        st.dataframe(city_msp(filtered_df))
    elif dataframe_selection == "Zip Code Prices":
        st.dataframe(zip_msp(filtered_df))

