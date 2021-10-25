import csv
from datetime import datetime
import requests
import base64
import json
import time
from selenium import webdriver


class YahooParser:
    def __init__(self, quote: str):
        """
        Init function of class YahooParser
        :param quote: Name of quote that will be using in this instance of class
        """
        self.quote = quote
        self.filepath = self.quote + ".csv"

    def parse_csv(self):
        """
        parses .csv file and return list
        :return: list of quote changes
        """
        quotes = {}
        f = open(self.filepath, "r")
        reader = csv.reader(f)
        for row in reader:
            if row[0] != "Date":
                quotes[row[0]] = {'Open': row[1], 'High': row[2], 'Low': row[3], 'Close': row[4], 'Adj Close': row[5],
                                  'Volume': row[6]}
        f.close()
        return quotes

    def get_quote(self):
        """
        downloading quote's .csv with requests
        :return: None or error in format (err_SOURCE_TYPE_ERROR+TEXT+FROM+EXCEPTION)
        """
        try:
            unixtime_now = str(int(datetime.now().timestamp()))
            # making request to yahoo and writing to .csv file
            url = f"https://query1.finance.yahoo.com/v7/finance/download/{self.quote}?period1=0&period2={unixtime_now}&interval=1d&events=history&includeAdjustedClose=true"
            f = open(self.filepath, "w")
            f.write(requests.get(url, headers={
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0"}).text)
            f.close()
        except Exception as e:
            return "err_generic_custom_"+str(e)

    def get_quote_selenium(self):
        """
        downloading quote's .csv with selenium
        (slowest way)
        :return: None or error in format (err_SOURCE_TYPE_ERROR+TEXT+FROM+EXCEPTION)
        """
        driver = webdriver.Firefox()
        try:
            driver.get(f"https://finance.yahoo.com/quote/{self.quote}/history")
            print("[+] started driver")
            try:
                driver.find_element("name", "agree").click()
                print("[+] clicked to agree on cookie request")
            except Exception as e:
                print("[-] Exception occurred on cookie request: " + str(e))

            driver.find_element("xpath", "//span[@class='C($linkColor) Fz(14px)']").click()
            print("[+] clicked to dropdown")
            driver.find_element("xpath", "//button[@data-value='MAX']").click()
            print("[+] clicked on MAX")
            try:
                download_element = driver.find_element("xpath", f"//a[@download='{self.quote}.csv']")
                download_url = download_element.get_property("href")
                if download_url is None:
                    print("[-] download link empty")
                    driver.close()
                    return "err_lnk_empty"

            except Exception as e:
                print("[-] error occurred when getting link: " + str(e))
                driver.close()
                return "err_lnk_custom_" + str(e)

            driver.execute_script("""
                window.file_contents = null;
                var xhr = new XMLHttpRequest();
                xhr.responseType = 'blob';
                xhr.onload = function() {
                    var reader  = new FileReader();
                    reader.onloadend = function() {
                        window.file_contents = reader.result;
                    };
                    reader.readAsDataURL(xhr.response);
                };
                xhr.open('GET', %(download_url)s);
                xhr.send();
            """.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ') % {
                'download_url': json.dumps(download_url),
            })
            print("[+] executed script")
            downloaded_file = None
            while downloaded_file is None:
                downloaded_file = driver.execute_script(
                    'return (window.file_contents !== null ? window.file_contents.split(\',\')[1] : null);')
                if not downloaded_file:
                    print('[*] not downloaded, waiting...')
                    time.sleep(0.5)
            print("[+] file downloaded")
            fp = open(self.filepath, 'wb')
            fp.write(base64.b64decode(downloaded_file))
            fp.close()
            print("[+] file written")
            driver.close()
        except Exception as e:
            driver.close()
            return "err_generic_custom_" + str(e)
