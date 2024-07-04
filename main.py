import requests_cache
from dotenv import dotenv_values
import os
import requests
import datetime as dt
from twilio.rest import Client

config = dotenv_values(".env")
stock_session = requests_cache.CachedSession("alphavantage_cache", expire_after=3600)

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
API_KEY_STOCK = config.get("API_KEY_STOCK")    # Get the API key from a local .env file with env. variables
API_KEY_NEWS = os.environ.get("API_KEY_NEWS")  # Get the API key from the PyCharm Run/Debug Configuration
TW_SID = config.get("TW_SID")
TW_AUTH = config.get("TW_AUTH")

PARAMETERS_STOCK = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": API_KEY_STOCK
}

PARAMETERS_NEWS = {
    "qInTitle": COMPANY_NAME,
    "sortBy": "publishedAt",
    "apiKey": API_KEY_NEWS
}


def get_news(percentage) -> None:
    response_news = requests.get("https://newsapi.org/v2/everything", params=PARAMETERS_NEWS)
    response_news.raise_for_status()
    data = response_news.json()["articles"]
    top_3 = data[:3]
    articles = [f"{STOCK}: {percentage}% {up_down} \n\nHeadline: {article['title']}. \n\nBrief: {article['description']}" for article in top_3]
    client = Client(TW_SID, TW_AUTH)
    for article in articles:
        client.messages.create(body=article, from_="+13343731335", to="+527771091313")

# Stock API call
response_stock = stock_session.get("https://www.alphavantage.co/query", params=PARAMETERS_STOCK)
response_stock.raise_for_status()
stock_data = response_stock.json()

yesterday = dt.datetime.today() - dt.timedelta(days=2)
before_yesterday = yesterday - dt.timedelta(days=1)

close_yesterday = float(stock_data["Time Series (Daily)"][str(yesterday.date())]["4. close"])
close_before_yesterday = float(stock_data["Time Series (Daily)"][str(before_yesterday.date())]["4. close"])
close_difference = abs(close_yesterday - close_before_yesterday)
diff_percentage = round((close_difference / close_yesterday) * 100, 2)

up_down = None
if close_difference > 0:
    up_down = "🔺"
else:
    up_down = "🔻"

if abs(diff_percentage) > 0.01:
    get_news(percentage=abs(diff_percentage))