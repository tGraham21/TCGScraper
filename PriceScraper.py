from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions
import statistics

import time
from dataclasses import dataclass

# Should let the user pass in field and the associated xpath instead of this
@dataclass
class PriceData:
    Title: str
    MarketPrice: str #As defined by TCGPlayer
    PrevSales: list


# TCGPlayer card price scraper. XPATH values are hard coded and won't work if website is updated.
# Need to pass in the card home page url for it to work
class PriceScraper:
    # pass in options or have defaults set
    def __init__(self, urls, options = None):
        self.urls = urls

        if(options == None):
            # irefox_options = webdriver.FirefoxOptions()
            # firefox_options.add_argument("-headless")
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--ignore-ssl-errors')
            chrome_options.add_argument('--headless=new')
        #else:
            #firefox_options = options
           
        self.driver = webdriver.Chrome(options=chrome_options)
    
    # returns mapping of url to associated PriceData
    def GetPriceData(self):
        output = {}

        for url in self.urls:

            self.driver.get(url)
            time.sleep(10)
            title = self.driver.title

            try:
                # hard coded. Will wait up to 15s for the element to load
                price = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'price') and @data-v-5fcceba6]"))).text

                if(price == "-"):
                    MarketPrice = None
                else:
                    MarketPrice = str(price[1:])

                saleElems= self.driver.find_elements(By.XPATH, "//span[contains(@class, 'price') and @data-v-0d2a5514]")

                PrevSales = []
                for elem in saleElems:
                    PrevSales.append(str(elem.text[1:]))
                
                if MarketPrice == None:
                    MarketPrice = statistics.median(PrevSales)
                    MarketPrice += "*"

            except selenium.common.exceptions.NoSuchElementException as e:
                raise Exception(e)

            output[url] = PriceData(title, MarketPrice, PrevSales)
        
        return output
    
    def Close(self):
        self.driver.close()






    

        
        