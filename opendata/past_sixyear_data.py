import pandas as pd
import os,re
import numpy as np


#找出指定路徑下的opendata檔案(生成為list)
data_file=os.listdir("D:\practice\house_price_comparison\opendata")
print(data_file)
#轉換表
trans = str.maketrans("一二三四五六七八九層有無全","123456789FYNA") 

#取出每一個檔名，若為.csv則讀取內容(清理資料)
for file in data_file:
    data_list=[]
    data_dict={}
    if ".csv" not in file:   #若檔案為.py則跳過
        continue
    #以utf8開啟
    with open (file,"r",encoding="utf8") as f:
        f1 = f.readlines()   #讀出來為一個list
    for f2 in f1[3:]:  #扣除每個檔案的前3行標題列，進行資料格式清理，一一放入data_list中
        pattern = r"\w+層,.*?/\w+層"   #查找符合層,*層的結構，若有，跳過該筆資料
        matches = re.search(pattern, f2)
        if matches:
            print(f2)
            continue
        if re.search(r"陽台,\w+層/\w+層", f2):
            f2 = f2.replace("陽台,","")
        if re.search(r"電梯樓梯間,\w+層/\w+層", f2):
            f2 = f2.replace("電梯樓梯間,","")
        if re.search(r"騎樓,\w+層/\w+層", f2):
            f2 = f2.replace("騎樓,","")

        f2 = f2.replace("\n","").strip(",").strip(";").split(",")  #將字串轉為list
        del f2[-1],f2[1],f2[0]  #刪除好清除且不要的資料
        #print(f2)
       
        times = 0  #計次
        while True:
            m1 = re.match(r"^[0-9/]{9}$" , f2[times])  #查找時間資料
            
            if m1:     #轉時間為西元
                a = f2[times][0:3]
                b = str(int(f2[times][0:3])+1911)
                f2[times] = f2[times].replace(a,b)
            
            elif re.search(r"/\w+層", f2[times]) :  #轉換樓層
                if "十層" in f2[times]:   #若內容有十層，將十層換成10F
                    f2[times] = f2[times].replace("十層","10F")
                if re.search(r"\w十\w層", f2[times]):   #若為幾十幾層，去除十
                    f2[times] = f2[times].replace("十","")
                if re.search(r"十\w層", f2[times]):     #若為十幾層，十變1
                    f2[times] = f2[times].replace("十","1")

                f2[times] = f2[times].translate(trans)   #其餘字符以轉換表轉換
                
            #如果找到字串+()的結構，且"建物" or "房地"不在其中時，僅取f2[times]在"("前的值(即房子type)
            if (re.search(r"\w+\(*\)", f2[times])) and ("建物" or "房地") not in f2[times]:
                f2[times] = f2[times].partition("(")[0]
                
            #若f2[times]=="無" or f2[times]=="有"，轉換字符
            if f2[times]=="無" or f2[times]=="有":
                f2[times] = f2[times].translate(trans)

            #若("建物" or "房地") in f2[times] 而且 times+1還在f2的index範圍的話，一次刪掉f2[times]及f2[times]後面欄
            if ("建物" or "房地") in f2[times] and times+1<len(f2):
                del f2[times+1],f2[times]
            elif  ("建物" or "房地") in f2[times]: #若times超出範圍，僅刪掉f2[times](最後備註欄)
                del f2[times]  

            times +=1
            #若times超出範圍，跳出迴圈
            if times >= len(f2):
                break
        #若尾巴沒清乾淨，清乾淨
        if len(f2)-12 == 2:
            del f2[-2],f2[-1]
        elif len(f2)-12 == 1 :
            del f2[-1] 
        elif len(f2)>12:
            print(f2)
            continue
           
        data_list.append(f2)  #只留下的資料 #把每筆寫完的file丟進pd
    df = pd.DataFrame(data_list,columns=["date","total_price(萬)","square(坪)","square_price(萬/坪)", \
                                         "主建物佔比","type","age","floor","格局","車位總價","管理組織","電梯"])     
    
    df["age"] = df["age"].replace("",None)
    df = df.drop(columns="車位總價")
    df = df.drop(columns="管理組織")
    #設定欄位類型，並設定float欄位小數點長度
    df["date"] = pd.to_datetime(df["date"],format="%Y/%m/%d")
    df["total_price(萬)"] = df["total_price(萬)"].astype(np.float32)
    df["square(坪)"] = df["square(坪)"].astype(np.float16)
    df["square(坪)"] =df["square(坪)"].apply(lambda x: round(x, 2))
    df["square_price(萬/坪)"] = df["square_price(萬/坪)"].astype(np.float32)
    df["square_price(萬/坪)"] =df["square_price(萬/坪)"].apply(lambda x: round(x, 2))
     
    print(df.dtypes,df)
    if "文山" in file:
        df.to_csv(f"D:\\practice\\house_price_comparison\\opendata\\refresh_data\\Wenshan_{file[3:7]}.csv",index=False,header = False,mode ="w")
    elif "新店" in file: 
        df.to_csv(f"D:\\practice\\house_price_comparison\\opendata\\refresh_data\\Xindian_{file[3:7]}.csv",index=False,header = False,mode ="a")

    

# df.to_csv("test.csv",index=False)



