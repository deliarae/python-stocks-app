import requests
import config
from datetime import date, timedelta


# --------- GENERAL -----------
# IFTTT Webhooks credentials, for now
event_name = ""
ifttt_id = "GYsVx2TL"


# Calculate the start and end dates in YYYY-MM-DD format for the 7-day period,
# with end_date being yesterday and start_date being 7 days ago.
today = date.today()
end_date = today - timedelta(days=1)
start_date = end_date - timedelta(days=6)

# --------- 7 DAY AVERAGE -----------
# Function to get the stock data from the last 7 days and return JSON response
def get_previous_7_days(api, start_date, today):
    tickers = "TSLA", "AAPL", "MSFT", "GOOG", "NKE"
    response = {}
    for ticker in tickers:
        url = f"https://api.twelvedata.com/time_series?symbol={ticker}&interval=1day&start_date={start_date}&end_date={today}&apikey={api}"
        response[ticker] = requests.get(url).json()
    return response

# Calculate the 7-day average price for each ticker
data_7_days = get_previous_7_days(config.api_key1, start_date, today)

for ticker, stock_data in data_7_days.items():
    closing_prices = [float(day['close']) for day in stock_data['values']]
    average = sum(closing_prices) / len(closing_prices)
    print(f"{ticker} Average Closing Price: {average}")
    

# --------- REAL-TIME PRICE -----------
# Function to retrieve real-time price
def get_realtime_price(api):
    tickers = "TSLA", "AAPL", "MSFT", "GOOG", "NKE"
    response = {}
    for ticker in tickers:
        url = f"https://api.twelvedata.com/price?symbol={ticker}&apikey={api}"
        response[ticker] = requests.get(url).json()
    return response

# Store real-time price data
data_realtime = get_realtime_price(config.api_key2)


# --------- MARKET OPEN PRICE -----------
# Function to get the market open, to compare real-time price to
def get_market_open(api, today):
    tickers = "TSLA", "AAPL", "MSFT", "GOOG", "NKE"
    response = {}
    for ticker in tickers:
        url = f"https://api.twelvedata.com/time_series?symbol={ticker}&interval=1day&outputsize=1&apikey={api}"
        response[ticker] = requests.get(url).json()
    return response

# Store market open price data
data_marketopen = get_market_open(config.api_key3, today)

# print for visualisation purposes:
for ticker, stock_data in data_marketopen.items():
    open_prices = [float(day['open']) for day in stock_data['values']]
    print(f"{ticker} Market Open: {open_prices}")

# --------- TRIGGER WEBHOOK IF CONDITION IS MET -----------
# Function to trigger IFTTT event
def trigger(event_name):
    url = f'https://maker.ifttt.com/trigger/{event_name}/with/key/{config.ifttt_key}'

    if requests.post(url).status_code == 200:
        print(f"Triggered the IFTTT applet for {event_name} successfully.")
        return
    
    print(f"Failed to trigger the IFTTT applet for {event_name}.")

# Map of tickers to event names
ticker_to_event = {
    "TSLA": "TSLA_Price_Drop",
    "AAPL": "AAPL_Price_Drop",
    "MSFT": "MSFT_Price_Drop",
    "GOOG": "GOOG_Price_Drop",
    "NKE": "NKE_Price_Drop"
}

# Assigning variance between market-open and real-time price
market_open_variance = 0.25

# Check conditions and trigger the corresponding event
for ticker, stock_data in data_realtime.items():
    current_price = float(stock_data['price'])
    event_name = ticker_to_event.get(ticker)
    market_open_price = float(data_marketopen[ticker]['values'][0]['open'])
    print(f"{ticker} Current Price: {current_price}")

    if current_price <= market_open_price - market_open_variance:
        trigger(event_name)
    elif current_price < average:
        trigger(event_name)
