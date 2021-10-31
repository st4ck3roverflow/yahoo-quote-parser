import csv
from datetime import datetime
import requests
import base64
import time
from selenium import webdriver
import sqlite3
from threading import Thread, Event
import json

import config


class YahooParser:
    def __init__(self, quote: str):
        """
        Init function of class YahooParser
        :param quote: Name of quote that will be using in this instance of class
        """
        self.quote = quote
        self.filepath = "temp.csv"

    @staticmethod
    def write_to_db(quotes_list):
        """
        Writes quote's info in database
        :param quotes_list: quotes in list format
        :return: None or error in format (err_SOURCE_ERROR+TEXT+FROM+EXCEPTION)
        """
        try:
            conn = sqlite3.connect(config.db_name)
            cursor = conn.cursor()

            for i in quotes_list:
                cursor.execute(f"drop table if exists {i}")
                cursor.execute(
                    f'create table {i} ("Date" "Date", "Open" "TEXT", "HIGH" "TEXT", "Low" "TEXT", "Close" "TEXT", "Adj Close" "TEXT", "Volume" "TEXT")')
                for g in quotes_list[i]:
                    data_info = quotes_list[i][g]
                    cursor.execute(
                        f"insert into {i} values ('{g}', '{data_info['Open']}', '{data_info['High']}', '{data_info['Low']}', '{data_info['Close']}', '{data_info['Adj Close']}', '{data_info['Volume']}');")
                conn.commit()
                conn.close()
        except Exception as e:
            return "err_writedb_" + str(e)

    def read_from_db(self):
        """
        Read quote's info from database
        :return: JSON formatted string with quote's info or error in format (err_SOURCE_ERROR+TEXT+FROM+EXCEPTION)
        """
        try:
            quotes = {}
            if self.quote == "*":
                for g in config.parsing_quotes:
                    quotes[g] = {}
                    conn = sqlite3.connect(config.db_name)
                    cursor = conn.cursor()
                    cursor.execute(f"select * from {g}")
                    qinfo = cursor.fetchall()
                    for i in qinfo:
                        quotes[g][i[0]] = {'Open': i[1], 'High': i[2], 'Low': i[3], 'Close': i[4],
                                           'Adj Close': i[5],
                                           'Volume': i[6]}
                qinfo_str = json.dumps(quotes)
                return qinfo_str
            else:
                quotes[self.quote] = {}
                conn = sqlite3.connect(config.db_name)
                cursor = conn.cursor()
                cursor.execute(f"select * from {self.quote}")
                qinfo = cursor.fetchall()
                for i in qinfo:
                    quotes[self.quote][i[0]] = {'Open': i[1], 'High': i[2], 'Low': i[3], 'Close': i[4],
                                                'Adj Close': i[5],
                                                'Volume': i[6]}
                qinfo_str = json.dumps(quotes)
                return qinfo_str
        except sqlite3.OperationalError:
            return "err_readdb_operationerr"
        # except Exception as e:
        #     return "err_readdb_generic_" + str(e)

    def parse_csv(self):
        """
        parses .csv file and return list
        :return: list of quote changes
        """
        try:
            quotes = {self.quote: {}}
            f = open(self.filepath, "r")
            reader = csv.reader(f)
            for row in reader:
                if row[0] != "Date":
                    quotes[self.quote][row[0]] = {'Open': row[1], 'High': row[2], 'Low': row[3], 'Close': row[4],
                                                  'Adj Close': row[5],
                                                  'Volume': row[6]}
            f.close()
            return quotes
        except Exception as e:
            return 'err_parsecsv_' + str(e)

    def update_quote(self):
        """
        downloading quote's .csv with requests
        :return: None or error in format (err_SOURCE_ERROR+TEXT+FROM+EXCEPTION)
        """
        try:
            unixtime_now = str(int(datetime.now().timestamp()))
            # making request to yahoo and writing to .csv file
            url = f"https://query1.finance.yahoo.com/v7/finance/download/{self.quote}?period1=0&period2={unixtime_now}&interval=1d&events=history&includeAdjustedClose=true"
            f = open(self.filepath, "w")
            quote_info = requests.get(url, headers={
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0"}).text
            if quote_info.startswith('404 Not Found'):
                return 'err_update_404nf'
            f.write(quote_info)
            f.close()
        except Exception as e:
            return "err_update_" + str(e)

    def update_quote_selenium(self):
        """
        downloading quote's .csv with selenium
        (slowest way)
        :return: None or error in format (err_SOURCE_ERROR+TEXT+FROM+EXCEPTION)
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
            quote_info = base64.b64decode(downloaded_file)
            if quote_info.startswith("404 Not Found"):
                return 'err_updatesel_404nf'
            fp = open(self.filepath, 'wb')
            fp.write(quote_info)
            fp.close()
            print("[+] file written")
            driver.close()
        except Exception as e:
            driver.close()
            return "err_updatesel_" + str(e)


class YahooDaemon(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._stop_event = Event()

    def is_stopped(self):
        return self._stop_event.is_set()

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self.is_stopped():
            for parsing_quote in config.parsing_quotes:
                print("[*] parsing: " + str(parsing_quote))
                parser_instance = YahooParser(parsing_quote)
                print("[+] made instance")
                if config.use_selenium:
                    answ = parser_instance.update_quote_selenium()
                    if answ is not None:
                        if answ == 'err_updatesel_404nf':
                            print('[-] quote not found')
                            continue
                        else:
                            print('[-] error occurred')
                            continue
                    print("[+] updated with selenium")
                else:
                    answ = parser_instance.update_quote()
                    if answ is not None:
                        if answ == 'err_update_404nf':
                            print('[-] quote not found')
                            continue
                        else:
                            print('[-] error occurred')
                            continue
                    print("[+] updated with requests")

                parsed_csv = parser_instance.parse_csv()
                print("[+] parsed csv")
                parser_instance.write_to_db(parsed_csv)
                print("[+] written to db")

            time.sleep(config.threading_interval)
