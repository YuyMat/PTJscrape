import requests
from bs4 import BeautifulSoup

from google.oauth2.service_account import Credentials
import gspread

import time


class Scraping(object):
    def __init__(self, url:str) -> None:
        response = requests.get(url)
        # 2. BeautifulSoupでHTMLをパースする
        self.soup: any = BeautifulSoup(response.text, 'html.parser')
        self.titles = self._get_titles()
        self.days = self._get_days()
        self.hours = self._get_hours()
        self.kind_of_jobs = self._get_kind_of_jobs()

    def _get_titles(self) -> list[str]:
        titles = self.soup.select("h3")
        rtn_titles = []
        for e in titles:
            rtn_titles.append(e.get_text())
        self._cleaning_list(rtn_titles)
        return rtn_titles
    
    def _get_days(self) -> list[str]:
        days = self.soup.select(".order-text span span")
        rtn_days = []
        for e in days:
            rtn_days.append(e.get_text())
        # clearning date
        rtn_days.pop(1)
        rtn_days.pop(0)

        return rtn_days
    
    def _get_hours(self) -> list[str]:
        hours = self.soup.select(".order-text span:nth-of-type(2)")
        tmp_hours = []
        for e in hours:
            tmp_hours.append(e.get_text())
        # clearning date
        tmp_hours.pop(1)
        tmp_hours.pop(0)
        
        rtn_hours = []
        for e in tmp_hours:
            rtn_hours.append(f"{e[4]}{e[6]}{e[7]}{e[8]}")
        
        return rtn_hours

    def _get_kind_of_jobs(self) -> list[str]:
        kinds = self.soup.select(".order-text span:nth-of-type(4)")
        rtn_kinds = []
        for e in kinds:
            rtn_kinds.append((e.get_text())[5:])
        # clearning date
        rtn_kinds.pop(1)
        rtn_kinds.pop(0)

        return rtn_kinds
    
    def _cleaning_list(self, what_list:list):
        what_list.pop(5)
        what_list.pop(4)
        what_list.pop(3)
        what_list.pop(1)
        what_list.pop(0)

class WriteGspread():
    def __init__(self, spreadsheetURL:str) -> None:
        scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
        ]
        credentials = Credentials.from_service_account_file(
            "/Users/yuya/Desktop/MyWork/scraping/gspread-442710-2a4434cd337c.json",
            scopes=scopes
        )
        gc = gspread.authorize(credentials)

        self.spreadsheet = gc.open_by_url(spreadsheetURL)
        self.spreadsheet = self.spreadsheet.sheet1
        
    
    def _write_value(self, cell:str, value:str) -> None:
        self.spreadsheet.update_acell(cell, value)

    def write_column(self, column:str, start:int, value:list):
        for i, v in enumerate(value):
            cell = f"{column}{start+i}"
            self._write_value(cell, v)
        
if __name__ == "__main__":
    spreadsheet_URL = "https://docs.google.com/spreadsheets/d/1IENxGyRWt3RD517U0hBwRlKPudVlftXE6-oBLxQQ8yk/edit?gid=0#gid=0"
    WG = WriteGspread(spreadsheet_URL)

    for i in range(20, 50):
        if (i == 0):
            scrape = Scraping('https://sharefull.com/jobs/tokyo/')
        else:
            scrape = Scraping(f'https://sharefull.com/jobs/tokyo/pages/{i+1}')

        WG.write_column('A', (21*i)+2, scrape.titles)
        WG.write_column('B', (21*i)+2, scrape.days)
        time.sleep(60)
        WG.write_column('C', (21*i)+2, scrape.hours)
        WG.write_column('D', (21*i)+2, scrape.kind_of_jobs)
        time.sleep(60)