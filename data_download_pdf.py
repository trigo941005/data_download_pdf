from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import os
import requests
from urllib.parse import urlparse, parse_qs, unquote
import time

def download_pdf(pdf_link, folder_name):
    try:
        # 解析 URL
        parsed_url = urlparse(pdf_link)
        
        # 從查詢參數中獲取 fileName，如果有的話
        query_params = parse_qs(parsed_url.query)
        
        # 檢查是否存在 'fileName' 參數，並提取它
        if 'fileName' in query_params:
            pdf_filename = query_params['fileName'][0]
        else:
            # 如果 URL 中沒有 fileName 參數，則退而求其次使用 URL 的路徑名
            pdf_filename = os.path.basename(unquote(parsed_url.path))
        
        # 確保資料夾存在
        file_path = os.path.join(folder_name, pdf_filename)
        
        # 下載 PDF 文件
        response = requests.get(pdf_link)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {file_path}")
        else:
            print(f"Failed to download: {pdf_link}")
    except Exception as e:
        print(f"Error occurred while downloading {pdf_link}: {e}")

def folder(folder_name):
    # 獲取當前執行程式的路徑
    current_directory = os.getcwd()

    # 組合路徑 (當前路徑 + 資料夾名稱)
    folder_path = os.path.join(current_directory, folder_name)

    # 如果資料夾不存在，則創建
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # 打印資料夾的路徑 (檢查資料夾是否創建成功)
    print(f"資料夾已創建於: {folder_path}")
    return folder_path

def search(name, data_type, year):
    driver = webdriver.Chrome()
    driver.get("https://mops.twse.com.tw/mops/web/t100sb11")
    driver.maximize_window()

    # 查詢下拉選單和輸入框，只執行一次
    select_element = driver.find_element(By.NAME, "skind")
    select = Select(select_element)
    year_input = driver.find_element(By.NAME, "year")
    
    for y in range(2):  # 根據需求爬取2個年度的資料
        folder_name = f"{name}_{data_type}_{year + y}"
        
        # 選擇工業類型
        select.select_by_value(data_type)
        time.sleep(1)
        
        # 清除並輸入年份
        year_input.clear()
        year_input.send_keys(str(year + y))
        print(f"查詢年份: {year + y}")
        
        # 點擊查詢按鈕
        button = driver.find_element(By.XPATH, "//input[@type='button' and @value=' 查詢 ']")
        button.click()
        
        # 等待加載完成
        time.sleep(3)
        
        # 找到所有的 <a> 標籤
        links = driver.find_elements(By.TAG_NAME, 'a')
        pdf_links = [link.get_attribute('href') for link in links if link.get_attribute('href') and '.pdf' in link.get_attribute('href')]
        
        # 滾動頁面以確保所有鏈接被加載
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        # 創建資料夾
        folder_path = folder(folder_name)
        
        # 下載每個 PDF 文件
        for pdf_link in pdf_links:
            download_pdf(pdf_link, folder_path)
    
    driver.quit()

# 外層迴圈控制不同類型的數據
name = "downloads"
data_types = ["01", "02", "03", "04"]
start_year = 110

# 遍歷每個類型
for data_type in data_types:
    search(name, data_type, start_year)
