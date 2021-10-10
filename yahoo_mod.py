import csv
from datetime import datetime
import requests


def get_quote_json(quote):
    unixtime_now = str(int(datetime.now().timestamp()))
    quotes = {}
    # making request to yahoo and writing to temp.csv
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{quote}?period1=0&period2={unixtime_now}&interval=1d&events=history&includeAdjustedClose=true"
    f = open("temp.csv", "w")
    f.write(requests.get(url, headers={
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0"}).text)
    f.close()
    # parsing csv
    f = open("temp.csv", "r")
    reader = csv.reader(f)
    for row in reader:
        if row[0] != "Date":
            quotes[row[0]] = {'Open': row[1], 'High': row[2], 'Low': row[3], 'Close': row[4], 'Adj Close': row[5], 'Volume': row[6]}
    f.close()
    return quotes


