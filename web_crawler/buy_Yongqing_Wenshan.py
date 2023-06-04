import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json,time
from random import randint
from selenium.webdriver.support.ui import WebDriverWait

#永慶房屋資料爬取
# search_url={"文山區":"台北市-文山區_c","新店區":"新北市-新店區_c"}
url="https://buy.yungching.com.tw/region/住宅_p/台北市-文山區_c/_rm/"

options = webdriver.ChromeOptions()
options.add_argument("incognito")
driver = webdriver.Chrome(options = options)
driver.get(url) # 所有文山區住宅的html

wait = WebDriverWait(driver, 15)
time.sleep(15)

# 找到最後一頁
last_page_link = driver.find_element(By.LINK_TEXT, "最末頁")
last_page_url = last_page_link.get_attribute("href")
last_page = int(last_page_url.split("pg=")[-1])

data = []

current_page = 1
while current_page <= last_page:
    print(f"開始爬取第{current_page}頁")
    wait = WebDriverWait(driver, 15)
    time.sleep(15)

    # 取得文山區第一頁的資料(住宅型態、屋齡、總坪數)
    soup = BeautifulSoup(driver.page_source,"html.parser")   #取動態原始碼          
    result = soup.find_all('li', class_='m-list-item')  #取最外面的class

    for obj in result:
        # 區域
        district = "文山區"

        # 屋齡、住宅型態、坪數(建坪)
        item_detail = obj.find('ul', {'class':'item-info-detail'})
        all_detail = item_detail.text.strip().replace('\n', '') #str

        pattern = r'([\u4e00-\u9fff]+).*?([\d.]+)年.*?建物 ([\d.]+)坪'
        matches = re.findall(pattern, all_detail, re.DOTALL)

        for match in matches:
            age = match[1].strip()
            type = match[0].strip()
            square = match[2].strip()

        # 總價
        total_price = obj.find('div', {'class':'price'}).text.replace('萬', '').replace(',', '')
        # print(total_price)

        # 單坪價格(總價/坪數) - float
        price =float(total_price)/float(square)
        square_price = round(price, 2)
        # print(square_price)

        # 篩選條件
        item_search = obj.find('div', {'class':'item-tags'}).find_all('span')
        # print(item_search)
        search = []
        for i in item_search:
            if i.text == '永慶房屋':
                continue
            search.append(i.text.replace("\n","").strip())
    
        data.append({
            'district': district,
            'age': age,
            'type': type,
            'square': square,
            'square_price': square_price,
            'total_price': total_price,
            'search': search
            })
    current_page = current_page + 1
    try:
        next_page = driver.find_element(By.LINK_TEXT, "下一頁 >")
        next_page.click()
    except:
        print("結束爬取資料～")
        
driver.quit()        

json_data = json.dumps(data, ensure_ascii=False)

# 將JSON格式資料寫入檔案
with open('永慶_文山區_買房.json', 'w', encoding='utf-8') as f:
    f.write(json_data)
