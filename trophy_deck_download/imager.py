from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pathlib import Path
import time
import shutil
import glob
import os

def make_image(txtname,imgname):
    # Chromeドライバを起動
    chrome_driver_path = "webdriver/chromedriver.exe"
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory" : str(Path("").resolve()),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True}
    options.add_experimental_option("prefs",prefs)
    #options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_driver_path, chrome_options=options)
    # 画面を取得しJavascriptが解決されるまで待機
    driver.get("https://mtg-decklistviewer.netlify.app/")
    
    # デッキテキスト読み込み
    deck_list = open(txtname, 'r')
    deck = deck_list.read()
    deck_list.close()

    elem_text = driver.find_element_by_xpath('//*[@id="input"]/textarea')
    elem_text.send_keys(deck)

    elem_view_btn = driver.find_element_by_xpath('//*[@id="buttonArea"]/button[1]')
    elem_view_btn.click()

    elem_dl_btn = driver.find_element_by_xpath('//*[@id="buttonArea"]/button[5]')
    elem_dl_btn.click()
    
    # Chromeドライバ終了
    time.sleep(30) # もっと賢いウェイト方法がある気がするが…
    driver.quit()

    # 移動
    shutil.move("decklist.png",imgname)

def make_image_folder():
    files = glob.glob("deck_txt/*/*/*")
    for line in files:
        print(line)

        #img_dir = os.path.join("deck_img","/".join(line.split("/")[1:2]))
        rank   = line.split("\\")[1]
        color  = line.split("\\")[2]
        deckid =line.split("\\")[3].split(".")[0]
        img_folder = os.path.join("deck_img",rank,color)
        img_filename = os.path.join(img_folder,deckid + ".png")
        print(img_folder)
        print(img_filename)

        # なければフォルダを作る
        if not os.path.exists(img_folder):
            os.makedirs(img_folder)
            
        # なければイメージを作る
        if not os.path.exists(img_filename):
            make_image(line,img_filename)

