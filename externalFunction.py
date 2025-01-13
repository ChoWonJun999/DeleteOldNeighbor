import os
import shutil
import time

import pyperclip
import undetected_chromedriver as uc
import tkinter as tk

from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

from fake_useragent import UserAgent
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_random_user_agent():
    ur = None
    try:
        ua = UserAgent(browsers=["chrome"], os=["windows"], platforms=["pc"])
        ur = ua.random
    except Exception as e:
        print(e)
    return ur


def chromeDriverSetting():
    chrome_options = webdriver.ChromeOptions()

    chrome_options.add_argument(f"user-agent={get_random_user_agent()}")  # 랜덤한 User-Agent 사용
    chrome_options.add_argument("Connection=close")

    # chrome_options.add_argument('--headless')  # 무감지 모드(백그라운드 실행)
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--disable-gpu')  # GPU 가속 비활성화
    chrome_options.add_argument('--no-sandbox')  # 필요한 옵션 추가

    caps = DesiredCapabilities.CHROME
    caps["pageLoadStrategy"] = "none"
    options = uc.ChromeOptions()

    # ChromeDriverManager 객체를 생성하기 전에 캐시 디렉토리를 삭제합니다.
    cache_path = ChromeDriverManager().install()
    cache_directory = os.path.dirname(cache_path)

    try:
        # 캐시 디렉토리를 삭제합니다.
        shutil.rmtree(cache_directory)
    except FileNotFoundError:
        print(f"Cache directory '{cache_directory}' not found.")

    return ChromeDriverManager().install(), options, chrome_options


def chromeDriverStart(CDM, options, chrome_options):
    driver = None
    try:
        driver_service = Service(CDM, options=options)

        driver = webdriver.Chrome(service=driver_service, options=chrome_options)
        driver.implicitly_wait(10)
    except Exception as e:
        print(e)

    return driver


def naverLogin(driver, user_id, user_pw):
    try:
        url = 'https://nid.naver.com/nidlogin.login?mode=form&url=https://www.naver.com/'
        driver.get(url)
        elem_id = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'id')))
        # elem_id = driver.find_element(By.ID, 'id')
        elem_id.click()
        pyperclip.copy(user_id)
        elem_id.send_keys(Keys.CONTROL, 'v')
        time.sleep(0.5)

        elem_pw = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'pw')))
        # elem_pw = driver.find_element(By.ID, 'pw')
        elem_pw.click()
        pyperclip.copy(user_pw)
        elem_pw.send_keys(Keys.CONTROL, 'v')
        time.sleep(0.5)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'log.login'))).click()
        # driver.find_element(By.ID, 'log.login').click()
        time.sleep(0.5)

        perv_url = 'https://nid.naver.com/nidlogin.login?mode=form&url=https://www.naver.com/'
        fail_login_url = 'https://nid.naver.com/nidlogin.login'
        # expected_url = 'https://www.naver.com/'

        # if expected_url in driver.current_url:
        if perv_url not in driver.current_url and fail_login_url not in driver.current_url:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


def findEl(driver, by, path):
    try:
        if by == "xpath":
            return driver.find_elements(By.XPATH, path)
        elif by == "id":
            return driver.find_element(By.ID, path)
    except TimeoutException:
        print("TimeoutException")
    except Exception as e:
        print(e)
    return None


def elLo(driver, by, path):
    try:
        if by == "css":
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, path)))
        # elif by == "xpath":
        else:
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, path)))
        return element
    except TimeoutException:
        print(f'path = {path}')
        print("TimeoutException")
    except Exception as e:
        print(f'path = {path}')
        print(e)
    return None


def elLoChildEl(driver, path):
    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, path)))

        child_div = element.find_elements(By.XPATH, './child::*')
        return child_div
    except TimeoutException:
        print(f'path = {path}')
        print("TimeoutException")
    except Exception as e:
        print(f'path = {path}')
        print(e)
    return None


def elementClick(driver, by, path):
    try:
        if by == "css":
            element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, path)))
        # elif by == "xpath":
        else:
            element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, path)))
        element.click()
    except TimeoutException:
        print(f'path = {path}')
        print("TimeoutException")
    except Exception as e:
        print(f'path = {path}')
        print(e)
    return None


def logInsert(obj, chk, msg):
    try:
        now = datetime.today()
        formatted_time = now.strftime("%H:%M:%S")
        obj.config(state=tk.NORMAL)
        if chk:
            obj.insert(tk.END, f'[{str(formatted_time)}] {msg}\n')
        else:
            obj.insert(tk.END, f'{msg}\n')
        obj.config(state=tk.DISABLED)
    except Exception as e:
        print(e)


def logDelete(obj):
    obj.config(state=tk.NORMAL)
    obj.delete("1.0", tk.END)
    obj.config(state=tk.DISABLED)


def update_button(obj, parameter, value):
    obj.config(state="normal")
    obj.config({f'{parameter}':f'{value}'})


def alertChk(driver):
    return EC.alert_is_present()(driver)
