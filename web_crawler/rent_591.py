from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json,time
from random import randint

#591租屋資料爬取
search_url={"文山區":"?region=1&section=12&searchtype=1","新店區":"?region=3&section=34&searchtype=1"}
house_type={"公寓":"1","電梯大樓":"2","透天厝":"3","別墅":"4"}
url="https://rent.591.com.tw/{}&showMore=1&shape={}"
# headers = {
# "Accept-Encoding":"gzip, deflate, br",
# "Accept":"*/*",
# "Accept-Language":"zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
# "Origin":"https://rent.591.com.tw",
# "Content-Type":"text/html",
# "Referer":"https://rent.591.com.tw/",
# "User-Agent":
# "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"}
options = webdriver.ChromeOptions()
options.add_argument("incognito")
driver = webdriver.Chrome(options = options)

all_data = []
for k,v in search_url.items():
    for keyword,housetype in house_type.items():
        index_page=0   #每一頁30個row，第一頁的row為0
        while True:
            url2=url.format(v,housetype)+f"&firstRow={index_page*30}"
            print(url2)
            driver.get(url2)
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")   #往下滑
            time.sleep(randint(5,20))  #休息幾秒

            soup = BeautifulSoup(driver.page_source,"html.parser")   #取動態原始碼          
            get_list = soup.find("section",class_="vue-list-rent-content")   #取項目內容，並檢查是否為空

            if get_list.text is None:  #若為空代表資料爬取完成，跳出
                break
            
            href = get_list.find_all("section",class_="vue-list-rent-item")  #取每一個項目
            for value in href:
                data ={"district":k,   #區域
                       "age":"null",   #屋齡(沒有屋齡資料)
                       "type":keyword,    #房屋種類
                       "square":None,    #坪數
                       "square_price":None,    #單坪價錢
                       "total_price":None,    #總價
                       "search":[]     #額外標籤
                       }  
                value2 = value.find("div",class_="rent-item-right")   #取每一個項目下的細項

                item_style = value2.find("ul",class_="item-style").find_all("li")
                item_tags = value2.find("ul",class_="item-tags").find_all("li")
                item_price = value2.find("div",class_="item-price").text
                print(item_price)
                data["total_price"]=int(item_price.replace("元/月","").replace(",","").strip())

                for b in item_tags:
                    b = b.text.replace(" ","").replace("\n","")
                    data["search"].append(b)
                for a in item_style:
                    if "坪" in a.text :
                        data["square"]=float(a.text.replace("坪","").strip())
                    else:
                        a = a.text.replace(" ","").replace("\n","")
                        data["search"].append(a)
                data["square_price"]=round(data["total_price"]/data["square"],2)
                
                all_data.append(data)
                print(data)
                
            index_page+=1
            
print(all_data)        

with open ("rent_591.json","w") as f:
    json.dump(all_data,f)
