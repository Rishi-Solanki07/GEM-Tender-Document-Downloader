#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Set up Selenium WebDriver and all libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import base64
from PIL import Image
from io import BytesIO
import pytesseract
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import requests
import glob
import fitz
import re
import pandas as pd
from pytesseract import image_to_string
import matplotlib.pyplot as plt
import pypdfium2 as pdfium


# In[2]:


# OPTIONAL: Set path to tesseract.exe if not in system PATH
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# In[3]:


# Set your download directory (where you want your information is get downloaded)
download_dir = r"C:\Users\solan\python_things\gempdf"


# In[4]:


# Set your browser where we are going to get information
#setup
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Optional: for headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")  # Usually for Linux, safe to keep
## please ignore the commnet part
# Disable PDF viewer in Chrome
#chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
#c
#hrome_options.add_argument('--disable-print-preview')


# In[5]:


# Set download behavior make sure the pdf get downloaded instead of opening
prefs = {
    "download.default_directory": download_dir,
    "plugins.always_open_pdf_externally": True,  # Download PDFs instead of opening in Chrome
}
chrome_options.add_experimental_option("prefs", prefs)


# In[6]:


# List of reference IDs (paste your reference_id over here)
reference_ids = [
    'GEM/2024/B/5588836',
    'GEM/2025/B/6071338',
    'GEM/2024/B/5594165',
    'GEM/2024/B/5458607',
    'GEM/2024/B/5480361',
    'GEM/2024/B/4560359',
    'GEM/2018/B/119037',
    'GEM/2022/B/1919736',
    'GEM/2024/B/5598504'
]

base_url = 'https://gem.gov.in/view_contracts/bid_detail?bid_no='


# In[7]:


# Step 3: Set up Selenium WebDriver (e.g., Chrome)
driver = webdriver.Chrome(options=chrome_options)  # Update with the path to your chromedriver


# In[8]:


# Store PDF data and show it after the information get downloaded
pdf_info_list = []

def wait_for_download_and_record(index, ref_id, download_dir):
    # Wait for .crdownload files to finish (max 20 seconds)
    for _ in range(20):
        cr_files = glob.glob(os.path.join(download_dir, "*.crdownload"))
        if not cr_files:
            break
        time.sleep(9)

    # Find the latest downloaded PDF
    pdf_files = glob.glob(os.path.join(download_dir, "*.pdf"))
    if not pdf_files:
        print(f"{ref_id} - PDF not found in folder!")
        return None

    latest_pdf = max(pdf_files, key=os.path.getctime)  # Get latest file
    original_pdf_name = os.path.basename(latest_pdf)

    print(f"{ref_id} - downloaded as {original_pdf_name}")

    return {
        "reference_id": ref_id,
        "pdf_name": original_pdf_name,
        "pdf_path": latest_pdf
    }


# In[9]:


# Loop through each reference ID
for index, ref_id in enumerate(reference_ids):
    full_url = base_url + ref_id
    driver.get(full_url)
    time.sleep(5)

    # Check if "No Result Found" exists
    try:
        no_result = driver.find_element(By.XPATH, "//div[contains(text(), 'No Result Found')]")
        print(f"{ref_id} - no result found")
        
        #  Append 'no result found' record
        pdf_info_list.append({
            "reference_id": ref_id,
            "pdf_name": "no result found",
            "pdf_path": "no result found"
        })
        
        continue
    except:
        pass  # No "No Result Found" message, proceed

    # Try to click to trigger captcha
    try:
        driver.find_element(By.CLASS_NAME, "ajxtag_order_number").click()
        time.sleep(5)
    except:
        print(f"{ref_id} - couldn't find contract number to click")
        continue

    # Loop to solve captcha
    for attempt in range(8):  # Try max 5 times
        try:
            # Get captcha image
            img_elem = driver.find_element(By.ID, "captchaimg")
            img_base64 = img_elem.get_attribute("src").split(",")[1]

            image = Image.open(BytesIO(base64.b64decode(img_base64)))
            captcha_text = pytesseract.image_to_string(image).strip()

            # Fill captcha
            driver.find_element(By.ID, "captcha_code").clear()
            driver.find_element(By.ID, "captcha_code").send_keys(captcha_text)

            # Submit
            driver.find_element(By.ID, "modelsbt").click()

            # Wait for download button
            wait = WebDriverWait(driver, 5)
            download_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#dwnbtn a")))
            download_link.click()

            print(f"{ref_id} - successfully downloaded")
            
            time.sleep(3)
            
            # ✅ Append download info
            pdf_info = wait_for_download_and_record(index, ref_id, download_dir)
            if pdf_info:
                pdf_info_list.append(pdf_info)
            else:
                #  No PDF found even after clicking download
                pdf_info_list.append({
                    "reference_id": ref_id,
                    "pdf_name": "no result found",
                    "pdf_path": "no result found"
                })
            
            time.sleep(6)
            break

        except:
            print(f"{ref_id} - captcha attempt {attempt + 1} failed, retrying...")
            try:
                refresh_btn = driver.find_element(By.XPATH, "//img[@src='/resources/images/refresh.png']")
                refresh_btn.click()
                time.sleep(6)
            except:
                print(f"{ref_id} - captcha refresh failed")
                break
    else:
        print(f"{ref_id} - failed after multiple captcha attempts")
        
        # ⛔ If captcha failed totally, mark as failed
        pdf_info_list.append({
            "reference_id": ref_id,
            "pdf_name": "captcha failed / no pdf",
            "pdf_path": "captcha failed / no pdf"
            
        })

# Close browser only if you want right now i make it as comment
#driver.quit()


# In[12]:


# Save output to CSV
rdf = pd.DataFrame(pdf_info_list)
# Set max column width to show full file paths
pd.set_option('display.max_colwidth', None)
rdf.head(10)


# In[15]:


#Save rdf DataFrame to CSV/excel format if you want
rdf.to_csv(r"C:\Users\solan\python_things\gempdf\info.csv", index=False)


# In[ ]:




