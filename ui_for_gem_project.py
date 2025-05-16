#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python
# coding: utf-8

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QLabel, QTextEdit, QPushButton, QWidget, QTableWidget, 
                            QTableWidgetItem, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys
import os
import glob
import time
import pandas as pd

# Import your existing script functions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import base64
from PIL import Image
from io import BytesIO
import pytesseract
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pypdfium2 as pdfium

class DownloadThread(QThread):
    update_signal = pyqtSignal(str, dict)
    finished_signal = pyqtSignal(list)
    
    def __init__(self, reference_ids, download_dir):
        super().__init__()
        self.reference_ids = reference_ids
        self.download_dir = download_dir
        self.running = True
        
    def run(self):
        pdf_info_list = []
        
        # Set up Chrome options (same as your original script)
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        
        prefs = {
            "download.default_directory": self.download_dir,
            "plugins.always_open_pdf_externally": True,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        driver = webdriver.Chrome(options=chrome_options)
        base_url = 'https://gem.gov.in/view_contracts/bid_detail?bid_no='
        
        for index, ref_id in enumerate(self.reference_ids):
            if not self.running:
                break
                
            full_url = base_url + ref_id.strip()  # Added strip() to clean whitespace
            driver.get(full_url)
            time.sleep(5)

            # Check if "No Result Found" exists
            try:
                no_result = driver.find_element(By.XPATH, "//div[contains(text(), 'No Result Found')]")
                self.update_signal.emit(f"{ref_id} - no result found", {
                    "reference_id": ref_id,
                    "pdf_name": "no result found",
                    "pdf_path": "no result found"
                })
                pdf_info_list.append({
                    "reference_id": ref_id,
                    "pdf_name": "no result found",
                    "pdf_path": "no result found"
                })
                continue
            except:
                pass

            # Try to click to trigger captcha
            try:
                driver.find_element(By.CLASS_NAME, "ajxtag_order_number").click()
                time.sleep(5)
            except:
                self.update_signal.emit(f"{ref_id} - couldn't find contract number to click", {
                    "reference_id": ref_id,
                    "pdf_name": "error - no contract number",
                    "pdf_path": "error - no contract number"
                })
                pdf_info_list.append({
                    "reference_id": ref_id,
                    "pdf_name": "error - no contract number",
                    "pdf_path": "error - no contract number"
                })
                continue

            # Loop to solve captcha
            for attempt in range(8):
                if not self.running:
                    break
                    
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

                    self.update_signal.emit(f"{ref_id} - successfully downloaded", {})
                    
                    time.sleep(3)
                    
                    # Wait for download to complete
                    pdf_info = self.wait_for_download_and_record(index, ref_id)
                    if pdf_info:
                        pdf_info_list.append(pdf_info)
                        self.update_signal.emit(f"{ref_id} - saved as {pdf_info['pdf_name']}", pdf_info)
                    else:
                        pdf_info_list.append({
                            "reference_id": ref_id,
                            "pdf_name": "no result found",
                            "pdf_path": "no result found"
                        })
                        self.update_signal.emit(f"{ref_id} - no PDF found after download", {
                            "reference_id": ref_id,
                            "pdf_name": "no result found",
                            "pdf_path": "no result found"
                        })
                    
                    time.sleep(6)
                    break

                except Exception as e:
                    msg = f"{ref_id} - captcha attempt {attempt + 1} failed, retrying..."
                    self.update_signal.emit(msg, {})
                    try:
                        refresh_btn = driver.find_element(By.XPATH, "//img[@src='/resources/images/refresh.png']")
                        refresh_btn.click()
                        time.sleep(6)
                    except:
                        self.update_signal.emit(f"{ref_id} - captcha refresh failed", {})
                        break
            else:
                self.update_signal.emit(f"{ref_id} - failed after multiple captcha attempts", {
                    "reference_id": ref_id,
                    "pdf_name": "captcha failed / no pdf",
                    "pdf_path": "captcha failed / no pdf"
                })
                pdf_info_list.append({
                    "reference_id": ref_id,
                    "pdf_name": "captcha failed / no pdf",
                    "pdf_path": "captcha failed / no pdf"
                })
        
        driver.quit()
        self.finished_signal.emit(pdf_info_list)
    
    def wait_for_download_and_record(self, index, ref_id):
        # Wait for .crdownload files to finish (max 20 seconds)
        for _ in range(20):
            cr_files = glob.glob(os.path.join(self.download_dir, "*.crdownload"))
            if not cr_files:
                break
            time.sleep(1)

        # Find the latest downloaded PDF
        pdf_files = glob.glob(os.path.join(self.download_dir, "*.pdf"))
        if not pdf_files:
            return None

        latest_pdf = max(pdf_files, key=os.path.getctime)  # Get latest file
        original_pdf_name = os.path.basename(latest_pdf)

        return {
            "reference_id": ref_id,
            "pdf_name": original_pdf_name,
            "pdf_path": latest_pdf
        }
    
    def stop(self):
        self.running = False

class GemPdfDownloaderUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GEM PDF Downloader")
        self.setGeometry(100, 100, 800, 600)
        
        # Main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)
        
        # Download directory selection
        self.dir_layout = QHBoxLayout()
        self.dir_label = QLabel("Download Directory:")
        self.dir_display = QLabel(os.path.expanduser("~/Downloads"))  # Default to Downloads
        self.dir_button = QPushButton("Change Directory")
        self.dir_button.clicked.connect(self.select_directory)
        
        self.dir_layout.addWidget(self.dir_label)
        self.dir_layout.addWidget(self.dir_display)
        self.dir_layout.addWidget(self.dir_button)
        self.layout.addLayout(self.dir_layout)
        
        # Reference IDs input
        self.ref_label = QLabel("Enter Reference IDs (comma-separated):")
        self.layout.addWidget(self.ref_label)
        
        self.ref_text = QTextEdit()
        self.ref_text.setPlaceholderText("GEM/2024/B/5588836, GEM/2025/B/6071338, ...")
        self.layout.addWidget(self.ref_text)
        
        # Buttons
        self.button_layout = QHBoxLayout()
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.start_download)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_download)
        self.stop_button.setEnabled(False)
        self.save_button = QPushButton("Save Results")
        self.save_button.clicked.connect(self.save_results)
        self.save_button.setEnabled(False)
        
        self.button_layout.addWidget(self.download_button)
        self.button_layout.addWidget(self.stop_button)
        self.button_layout.addWidget(self.save_button)
        self.layout.addLayout(self.button_layout)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.layout.addWidget(self.status_label)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Reference ID", "PDF Name", "PDF Path"])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.layout.addWidget(self.results_table)
        
        # Initialize variables
        self.download_thread = None
        self.results_data = []
        
    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Download Directory")
        if directory:
            self.dir_display.setText(directory)
    
    def start_download(self):
        # Get comma-separated IDs and split them
        input_text = self.ref_text.toPlainText().strip()
        reference_ids = [ref.strip() for ref in input_text.split(',') if ref.strip()]
        
        if not reference_ids:
            QMessageBox.warning(self, "Warning", "Please enter at least one reference ID")
            return
            
        download_dir = self.dir_display.text()
        if not os.path.exists(download_dir):
            QMessageBox.warning(self, "Warning", "The specified download directory does not exist")
            return
            
        # Disable UI elements during download
        self.download_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.save_button.setEnabled(False)
        self.status_label.setText("Downloading...")
        
        # Clear previous results
        self.results_table.setRowCount(0)
        self.results_data = []
        
        # Start download thread
        self.download_thread = DownloadThread(reference_ids, download_dir)
        self.download_thread.update_signal.connect(self.update_status)
        self.download_thread.finished_signal.connect(self.download_finished)
        self.download_thread.start()
    
    def stop_download(self):
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.stop()
            self.status_label.setText("Download stopped by user")
            self.download_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.save_button.setEnabled(True)
    
    def update_status(self, message, data):
        self.status_label.setText(message)
        
        if data and 'reference_id' in data:
            # Add to results table
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            
            self.results_table.setItem(row, 0, QTableWidgetItem(data['reference_id']))
            self.results_table.setItem(row, 1, QTableWidgetItem(data['pdf_name']))
            self.results_table.setItem(row, 2, QTableWidgetItem(data['pdf_path']))
            
            # Add to results data for saving
            self.results_data.append(data)
    
    def download_finished(self, pdf_info_list):
        self.status_label.setText("Download completed")
        self.download_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.save_button.setEnabled(True)
        
        # Ensure all results are in the table
        self.results_data = pdf_info_list
        self.results_table.setRowCount(0)
        for data in pdf_info_list:
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            
            self.results_table.setItem(row, 0, QTableWidgetItem(data['reference_id']))
            self.results_table.setItem(row, 1, QTableWidgetItem(data['pdf_name']))
            self.results_table.setItem(row, 2, QTableWidgetItem(data['pdf_path']))
    
    def save_results(self):
        if not self.results_data:
            QMessageBox.warning(self, "Warning", "No results to save")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "", "CSV Files (*.csv);;Excel Files (*.xlsx)")
            
        if file_path:
            df = pd.DataFrame(self.results_data)
            if file_path.endswith('.xlsx'):
                df.to_excel(file_path, index=False)
            else:
                df.to_csv(file_path, index=False)
            QMessageBox.information(self, "Success", "Results saved successfully")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set tesseract path if needed (uncomment and modify if required)
    # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    
    window = GemPdfDownloaderUI()
    window.show()
    sys.exit(app.exec_())

