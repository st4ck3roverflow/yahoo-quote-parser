# yahoo-quote-parser
Yahoo quote parser made on Flask

Every 10 seconds parse Yahoo Finance quotes in a list that marked in config.py.
By API, you can get quote's info from database.
#Configuration
If you want to use selenium instead requests, in config.py set:
```python
use_selenium = True
```
To set parsing quotes in config.py change this list:
```python
parsing_quotes = ["PD", "ZUO", "PINS", "ZM", "DOCU", "CLDR", "RUN"]
```
To set parsing interval change this in config.py:
```python
threading_interval = 100  # in seconds
```
# API Usage
Get quote info in JSON format
```http request
/get_quote?quote=QUOTE_NAME
```
Get all quotes info in JSON format
```http request
/get_quote?quote=*
```
# Build
```
docker build --tag yahoo-parser .
docker run --publish 5000:5000 yahoo-parser
```
#Contact
https://arturyud.in/itsme
