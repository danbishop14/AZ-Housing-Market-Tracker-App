# Housing Market Snapshot

This Streamlit app provides a snapshot of the current state of the housing market in Arizona. It includes information on median sale price, number of homes sold, and the average 30-year fixed mortgage rate for the state. Users can also view data from the S&P/Case-Shiller Home Price Index, which tracks changes in home values in the U.S.

## Features
![Market_Snapshot_IMG](https://user-images.githubusercontent.com/69700884/210016967-8d86b157-410b-483d-b0fe-cb684166ba09.JPG)

- View detailed information about the housing market in Arizona by city or zip code
- See changes in housing market metrics from the previous month
- View the latest Case-Shiller Home Price Index value, as well as the month-over-month (MoM) and year-over-year (YoY) changes
- View a table with detailed information about the Case-Shiller Home Price Index calculations

## Requirements

To run this app, you will need to have the following dependencies installed:

- Streamlit
- Any other libraries or modules used in the app code (e.g. Pandas, NumPy, etc.)
- Pandas
- Requests

You will also need to obtain an API key from the Federal Reserve Economic Data (FRED) website in order to access the Case-Shiller Home Price Index data.

## Running the App

To run the app, clone the repository to your local machine and navigate to the directory containing the app code. Then, create a virtual environment and install the required dependencies. Finally, update the `fred_api` variable with your FRED API key and run the following command:

```bash
streamlit run Market_Snapshot.py
