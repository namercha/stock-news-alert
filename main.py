import requests
import os
from twilio.rest import Client

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
STOCK_API_KEY = os.environ.get("STOCK_API_KEY")
stock_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "outputsize": "compact",
    "apikey": STOCK_API_KEY,
}

NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

account_sid = os.environ.get("TWILIO_ACCOUNT_SID")  # Twilio account SID
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")  # Twilio auth token
from_phone_number = os.environ.get("TWILIO_PHONE_NUMBER")  # Twilio phone number
to_phone_number = os.environ.get("MY_PHONE_NUMBER")  # Your phone number to get the SMS message.

## STEP 1: Use https://www.alphavantage.co/documentation/#daily
# When stock price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

# 1. - Get yesterday's closing stock price. Hint: You can perform list comprehensions on Python dictionaries.
#  e.g. [new_value for (key, value) in dictionary.items()]
response = requests.get(url=STOCK_ENDPOINT, params=stock_parameters)
response.raise_for_status()
prices = response.json()["Time Series (Daily)"]
prices_list = [value for (key, value) in prices.items()]
yesterdays_closing_price = float(prices_list[0]["4. close"])

# 2. - Get the day before yesterday's closing stock price
day_before_yesterdays_closing_price = float(prices_list[1]["4. close"])

# 3. - Find the positive difference between 1 and 2. e.g. 40 - 20 = -20, but the positive difference is 20.
#  Hint: https://www.w3schools.com/python/ref_func_abs.asp
price_difference = yesterdays_closing_price - day_before_yesterdays_closing_price
up_down = None
if price_difference > 0:
    up_down = "🔺"
else:
    up_down = "🔻"

# 4. - Work out the percentage difference in price between closing price yesterday and closing price the day
#  before yesterday.
percent_difference = round(100 * price_difference / yesterdays_closing_price)
print(percent_difference)

# 5. - If TODO4 percentage is greater than 5 then print("Get News").
if abs(percent_difference) > 1:
    print("Get News")
    ## STEP 2: https://newsapi.org/
    # Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.
    # 6. - Instead of printing ("Get News"), use the News API to get articles related to the COMPANY_NAME.
    news_parameters = {
        "apikey": NEWS_API_KEY,
        "qInTitle": COMPANY_NAME
    }
    response = requests.get(url=NEWS_ENDPOINT, params=news_parameters)
    articles = response.json()["articles"]

    # 7. - Use Python slice operator to create a list that contains the first 3 articles. Hint:
    #  https://stackoverflow.com/questions/509211/understanding-slice-notation
    three_articles = articles[:3]

    ## STEP 3: Use twilio.com/docs/sms/quickstart/python
    # to send a separate message with each article's title and description to your phone number.

    # 8. - Create a new list of the first 3 article's headline and description using list comprehension.
    formatted_articles = [f"{STOCK_NAME}: {up_down}{percent_difference}%\n Headline: {articles['title']}. \nBrief: {articles['description']}" for item in
                          three_articles]

    # 9. - Send each article as a separate message via Twilio.
    client = Client(account_sid, auth_token)
    for article in formatted_articles:
        message = client.messages \
            .create(
            body=article,
            from_=from_phone_number,
            to=to_phone_number
        )

# Format the message like this:
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""
