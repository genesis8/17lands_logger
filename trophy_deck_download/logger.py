import urllib.request
import sys
import os

# url   : Web上のファイルパス
# name  : ファイル名
# rank  : ディレクトリ名(1)ランク
# color : ディレクトリ名(2)カラー
def download_file(url,name,rank,color):
    dl_dir = "deck_txt"
    dirpath = os.path.join(dl_dir,rank,color)
    # ディレクトリが無ければ作る
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    filepath = os.path.join(dirpath,name)
    urllib.request.urlretrieve(url,filepath)

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def get_trophy_decks_info():
    # Chromeドライバを起動
    chrome_driver_path = "webdriver/chromedriver.exe"
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_driver_path, chrome_options=options)
    # 画面を取得しJavascriptが解決されるまで待機
    driver.get("https://www.17lands.com/trophies")
    driver.implicitly_wait(5)
    # デッキリストのテーブルから情報取得
    element = driver.find_element_by_xpath('//*[@id="trophies_app"]/div/table/tbody')
    html = element.get_attribute('innerHTML')
    soup = BeautifulSoup(html,"html.parser")
    blocks = soup.find_all("tr")
    for block in blocks:
        # HTMLから必要情報を抽出
        columns = block.find_all("td")
        rank    = columns[3].get_text().split("-")[0]
        color   = columns[4].find("span")["title"]
        url     = columns[5].find_all("a")[1]["href"]

        # 保存処理に必要な情報を作成
        key     = url.split(r"/")[2]
        texturl = "https://www.17lands.com" + url + ".txt"
        textname = key + ".txt"
        print(url , textname , rank , color)
        # 保存
        download_file(texturl,textname,rank,color)
    
    # Chromeドライバ終了
    driver.quit()
