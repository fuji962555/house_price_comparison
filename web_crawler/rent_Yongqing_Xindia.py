import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import json,time
from random import randint
from selenium.webdriver.support.ui import WebDriverWait

#永慶租屋資料爬取
url = "https://rent.yungching.com.tw/"

options = webdriver.ChromeOptions()
options.add_argument("incognito")
driver = webdriver.Chrome(options = options)
driver.get(url)

wait = WebDriverWait(driver, 10)
dataOption = driver.find_element(By.XPATH, '//span[@title="新北市" and text()="新北"]')
dataOption.click()
time.sleep(10)

wait = WebDriverWait(driver, 10)
dataOption = driver.find_element(By.XPATH, '//span[@title="新店區" and text()="新店區"]')
dataOption.click()
time.sleep(10)

soup = BeautifulSoup(driver.page_source,"html.parser")
result = soup.find_all('div', class_='house_block')  

data = []

while True:

    soup = BeautifulSoup(driver.page_source, "html.parser")
    result = soup.find_all('div', class_='house_block')

    for obj in result:
        # 區域
        district = "新店區"

        # 屋齡
        age = "null"

        # 住宅型態
        type_detail = obj.find('ul', {'class':'houseul02'}).text
        type = type_detail.replace('型態：', '')
        # print(type)

        # 坪數(建坪)
        square_detail = obj.find('ul', {'class':'houseul01'}).text
        pattern = r'坪數：(\d+\.\d+) 坪'
        match = re.search(pattern, square_detail)
        square = match.group(1)
        # print(square)

        # 總價
        price_detail = obj.find('p', {'class':'price'}).text
        total_price = price_detail.rstrip(' 元/月').replace(',', '')
        # print(total_price)

        # 單坪價格
        price = float(total_price)/float(square)
        square_price = round(price, 2)

        # 篩選條件
        search = "null"

        data.append({
            'district': district,
            'age': age,
            'type': type,
            'square': square,
            'square_price': square_price,
            'total_price': total_price,
            "search": search
        })

    try: # 嘗試做點下一頁這件事
        next_page = driver.find_element(By.XPATH, '//li/a[@class="cht" and text()="下一頁"]')
        next_page.click()
        time.sleep(10)
    except: # 如果沒有下一頁就跳出迴圈
        print("結束爬取資料～")
        break 


json_data = json.dumps(data, ensure_ascii=False)

# 將JSON格式資料寫入檔案
with open('永慶_新店_租房.json', 'w', encoding='utf-8') as f:
    f.write(json_data)
