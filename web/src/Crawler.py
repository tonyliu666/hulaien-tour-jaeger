import bs4 
import os 
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
# from subprocess import CREATE_NO_WINDOW
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from xvfbwrapper import Xvfb
from time import sleep
# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager
host =  os.environ.get('SELENIUM_REMOTE_HOST')
vdisplay = Xvfb()
d = DesiredCapabilities.CHROME 
d['platform'] = "LINUX"
d['loggingPrefs'] = {'performance': 'ALL'}
Options = webdriver.ChromeOptions()
Options.add_argument('--no-sandbox')
    # Options.add_argument('--headless')
Options.add_argument('--blink-settings=imagesEnabled=false')
def remote():
    vdisplay.start()
    driver = webdriver.Remote ( 
    command_executor= f'http://{host}:4444/wd/hub',
    desired_capabilities= d , 
    options = Options,
    )
    vdisplay.stop()
    return driver 
# driver = webdriver.Chrome() 
# driver.get(f"http://{host}:4444/wd/hub")
class crawl(str): 
    def data(self,name):
        from urllib.request import urlopen
        with urlopen(name) as response:
            data = response.read().decode("utf-8")
            root= bs4.BeautifulSoup(data,'html.parser')
            text = root.find_all("meta",{"itemprop":"description"},"content")[0]["content"]
            url = root.find("a",{"target":"_blank"})["href"]
            result = root.find_all('div',{"class":"point_list"})
            if len(result) == 1:
                traffic = result[0].div.p.text
                address = root.find("a",{"target":"_blank"}).span
                if address ==None:
                    return [text,traffic,url]
                else:
                    address= address.text
                    return [text,address,traffic,url] 
            elif len(result) == 0: 
                address = root.find("div",{"class":"address"})
                if address ==None:
                    return [text]
                else: 
                    address = address.p.span.text
                    return [text,address]
            else:   
                address = root.find("a",{"target":"_blank"}).span.text
                opening_time = result[0].p.text
                fee = result[1].p.text
                return [text,address,opening_time,fee,url]
    def google_search(self,name):#這是好的
        driver = remote()
        driver.get(name)
        # sleep(5)
        driver.implicitly_wait(10)
        # WebDriverWait(driver, timeout=10).until()
        source = driver.page_source
        root= bs4.BeautifulSoup(source,'html.parser')
        # text = root.find_all("div",{"class":"f4hh3d"},limit=5)
        text = root.find_all("div",{"class":"f4hh3d"})
        img_stars = []
        for i in text:
            src = i.find("div",{"class":"kXlUEb"})
            src = src.find("easy-img",{"class":"dBuxib SCkDmc"})
            try :
                src= src.img['src']
            except:
                src = src.img['data-src']
            fig = i.find("div",{"class":"GwjAi"}) #fig:位置
            comment = fig.find("div",{"class":"nFoFM"}).text
            fig = fig.find("div",{"class":"rbj0Ud AdWm1c"})
            fig = fig.find("div",{"class":"skFvHc YmWhbc"}).text
            stars = i.find("div",{"class":"GwjAi"})
            stars= stars.find("div",{"class":"tP34jb"})
            try : 
                stars = stars.span["aria-label"]
            except :
                stars = None
            # print(fig,sys.stderr)
            # print(stars,sys.stderr)
            # stars = stars.find("span",{"class":"ta47le"})["aria-label"]
            img_stars.append([fig,stars,comment,src])
        driver.quit()
        return img_stars
    def tour_guide(self,name):
        # options = webdriver.ChromeOptions()
        # options.add_argument('--no-sandbox')
        # options.add_argument('--headless')
        # driver = webdriver.Remote(
        #     command_executor='http://selenium-hub:4444/wd/hub',
        #     # options=webdriver.ChromeOptions()
        #     desired_capabilities=options.to_capabilities(),
        # )
        # driver.get(name)
        driver = remote()
        driver.get('https://www.google.com/search?q='+name)
        # sleep(5)
        driver.implicitly_wait(10)
        source = driver.page_source
        root= bs4.BeautifulSoup(source,'html.parser')
        text = root.find_all("div",{"class":"yuRUbf"},limit=5)
        url_list = []
        for i in text:
            url_list.append(i.a['href'])
        driver.quit()
        return url_list
    def __init__ (self,name):
        self.name = name 
class selenium(str):
    def data(self,name): 
        # serv = ChromeService(ChromeDriverManager(version='104').install())
        # serv.creationflags = CREATE_NO_WINDOW
        # options = webdriver.ChromeOptions()
        # options.add_argument('--no-sandbox')
        # options.add_argument('--headless')
        # driver = webdriver.Remote(
        #     # command_executor='http://selenium-hub:4444/wd/hub',
        #     command_executor='http://selenium-hub:4444/wd/hub',
        #     # options=webdriver.ChromeOptions()
        #     desired_capabilities=options.to_capabilities(),
        # )
        # driver.get(name)
        driver = remote() 
        driver.get('https://www.booking.com/')
        # sleep(5)
        driver.implicitly_wait(30)
        # WebDriverWait(driver, timeout=10).until()
        try:   
            # search = WebDriverWait(driver,45).until(
            #     EC.presence_of_element_located((By.ID,"ss"))
            # )
            search = driver.find_element(By.ID,"ss")
            search.send_keys(name)
            search.send_keys(Keys.ENTER)
            sleep(10)
            source = driver.page_source
            root= bs4.BeautifulSoup(source,'html.parser')
            text = root.find_all("div",{"data-testid":"property-card"},limit=5)
        finally:
            driver.quit()
        return text
    def __init__(self,name):
        self.name = name 
class store():
    List = []
    def list_back():
        return store.List
class fig_store():
    fig = [] 
    set = False
    def fig_back():
        return fig_store.fig
    def set_back():
        return fig_store.set
class click_store():
    set = False 
    def set_back():
        return click_store.set