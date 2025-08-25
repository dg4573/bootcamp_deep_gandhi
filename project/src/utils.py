import re
import time
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from pyotp import TOTP
from SmartApi import SmartConnect
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os


api_key = "q3NHa6rL"
client_code = "D531034"
pwd = "1123"
totp = "MKFRGXBJ66GCDC2U3BP4LLKMWM"


# =================== Helper Functions =============================
def chdir_data():
    os.chdir(r"C:\Users\Lenovo\Jupyter Notebooks\Trading")

# =================== IV Surface ===================================
def connect_api():
    obj = SmartConnect(api_key=api_key)
    session = obj.generateSession(client_code, pwd, TOTP(totp).now())
    refreshToken = session['data']['refreshToken']
    obj.generateToken(refreshToken)
    return obj

def fetch_data(obj):
    expirydate_l = ["21AUG2025", "28AUG2025", "02SEP2025", "09SEP2025"]
    ce_df, pe_df = pd.DataFrame(), pd.DataFrame()
    try:
        for expirydate in expirydate_l:
            time.sleep(1)
            greek_params = {"name": "NIFTY", "expirydate": expirydate}
            greek_res = obj.optionGreek(greek_params)
            greek_df = pd.DataFrame(greek_res['data'])
            ce_df = pd.concat([ce_df, greek_df[greek_df['optionType'] == "CE"]], ignore_index=True)
            pe_df = pd.concat([pe_df, greek_df[greek_df['optionType'] == "PE"]], ignore_index=True)
        chdir_data()
        ce_df.to_csv("data/ce_df.csv")
        pe_df.to_csv("data/pe_df.csv")
    except:
        chdir_data()
        ce_df = pd.read_csv("data/ce_df.csv")
        pe_df = pd.read_csv("data/pe_df.csv")
    return ce_df, pe_df

def preprocess_data(ce_df, pe_df):
    for df in [ce_df, pe_df]:
        df['impliedVolatility'] = pd.to_numeric(df['impliedVolatility'], errors='coerce')
        df.dropna(subset=['impliedVolatility'], inplace=True)
        df = df[df['impliedVolatility'] > 0]
    today = datetime.today()
    ce_df['dte'] = ce_df['expiry'].apply(lambda x: (datetime.strptime(x, "%d%b%Y") - today).days)
    pe_df['dte'] = pe_df['expiry'].apply(lambda x: (datetime.strptime(x, "%d%b%Y") - today).days)
    return ce_df, pe_df

def make_pivots(ce_df, pe_df):
    pivot_ce = ce_df.pivot_table(index='dte', columns='strikePrice', values='impliedVolatility')
    pivot_pe = pe_df.pivot_table(index='dte', columns='strikePrice', values='impliedVolatility')
    return pivot_ce, pivot_pe

def make_surface(pivot, title, colorscale):
    x, y, z = pivot.columns.values, pivot.index.values, pivot.values
    fig = go.Figure(data=[go.Surface(x=x, y=y, z=z, colorscale=colorscale)])
    fig.update_layout(
        title=title,
        width=1000,
        height=700,
        margin=dict(l=20, r=20, t=40, b=20),
        scene=dict(xaxis_title='Strike Price', yaxis_title='Days to Expiry',zaxis_title='Implied Volatility (%)', 
                   aspectmode='manual',aspectratio=dict(x=1.5, y=1, z=0.7),camera=dict(eye=dict(x=1.5, y=1.5, z=1))))
    return fig

# =============================== IV Rank and Percentile ==================================

def click_apply(driver):
    '''Click 'Apply' Button on website after choosing
    appropriate date from calendar'''
    driver.find_element(By.XPATH, '//button[text()="Apply"]').click()
    return "Changes Applied!"

def click_day(day_number, wait):
    '''Click the day number in the calendar'''
    xpath = f"//button[@name='day' and text()='{day_number}']"
    button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    button.click()
    return f"Clicked day {day_number}"

def calculate_iv_rank_pct(points, slope, intercept, days):
    '''Calculates IV Rank and Percentile for a given number of days
    (Max days is len(points)~252 for now), 
    Days = no. trading days'''
    if days > len(points):
        return f"Max days data available is {len(points)} days."
    points = points[-days:]
    values = [(slope * i[1]) + intercept for i in points]
    values = np.array(values)
    current_iv = values[-1]
    iv_min = np.min(values)
    iv_max = np.max(values)
    iv_rank = (current_iv - iv_min) / (iv_max - iv_min) * 100
    iv_percentile = np.sum(values < current_iv) / len(values) * 100
    return iv_rank, iv_percentile

def fetch_points():
    URL = "https://web.sensibull.com/implied-volatility-chart?underlying=NIFTY"
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/115.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(URL)
    wait = WebDriverWait(driver, 60)
    wait.until(EC.element_to_be_clickable((By.ID, "Line"))).click()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-controls="radix-10"]'))).click()
    button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.month-nav-btn")))
    for _ in range(11):
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.month-nav-btn")))
        button.click()
        time.sleep(0.5)
    today = date.today()
    one_year_ago = today - timedelta(days=365)
    weekday = one_year_ago.weekday()
    if weekday == 5:     
        one_year_ago += timedelta(days=2)
    elif weekday == 6:   
        one_year_ago += timedelta(days=1)  
    day_number = str(one_year_ago)[-2:]
    print(click_day(day_number, wait))
    print(click_apply(driver))
    d = driver.find_element(By.CSS_SELECTOR, 'path.visx-linepath[stroke="var(--ivLineColor)"]').get_attribute("d") 
    coords = re.findall(r'[-+]?\d*\.\d+|\d+', d)
    points = [(float(coords[i]), float(coords[i+1])) for i in range(0, len(coords), 2)]
    driver.quit()
    return points

def slope_intercept(points, v1, v2):
    y1 = points[0][1]
    y2 = points[-1][1]
    slope = (v2 - v1) / (y2 - y1)
    intercept = v1 - (slope * y1)
    return slope, intercept

def display_iv_rank():
    points = fetch_points()
    v1 = 12.11 # Index 0 (First IV)
    v2 = 11.79 # Index -1 IV (Last IV)
    slope, intercept = slope_intercept(points, v1, v2)
    days_to_display = [7, 15, 20, 30, 100, len(points)]
    results = {}
    for d in days_to_display:
        results[d] = calculate_iv_rank_pct(points, slope, intercept, d)
    return results


