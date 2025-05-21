# GEM-Tender-Document-Downloader


## Problem Statement
a company call 'abc ltd' is a service provider for tender information and they have clients from all over the india subscribe to thier services, on gem website we have tender informations
our Customer support teams handling Government e-Marketplace (GEM) portal queries face a significant challenge when clients report on call they can see tender winner bidder information on abc ltd portal for xyz tenders but cannot download the documents for that particual tender and client send mutiple cases, so support team needs to deal with each tender's reference id.
 - each tender has unique reference id
 - if we have winner bidder name on gem, document must be upload as a pdf
 - not applicable when reference id is wrong
 - when officially gem site is not uploaded document this method won't work

# please check my presentation for more understanding [Click-here](https://drive.google.com/file/d/1f8yoK-Sas3PNsCIJRsyIhFy0Iqh2GM_T/view?usp=sharing)

1. **customer Support employee must manually:**
   - Visit https://gem.gov.in/
   - Search for each tender using its unique reference ID
   - Solve captchas repeatedly for each tender
   - Download documents one-by-one
   - Verify successful downloads
   - Send documents to clients

2. **This becomes time-consuming when handling client's on call:**
   - 2-3 reference IDs (typical case)
   - 30-40 reference IDs (large cases)
   - Multiple clients simultaneously

3. **Additional complications:**
   - Not all customer support employee have direct database access
   - Senior agents get overloaded with more work
   - Clients remain on hold during manual verification



## to solves these issues  we can just  enable one-click downloading of all tender documents using reference IDs, and you will get your documents downloaded on your choosen path.
## yes! paste your all reference ids given by client and run the code and you will get your all tender's documents in minutes, let me explain my code.

## How the Solution Works

### Step 1: Initialization and Setup
**Libraries Used:**
- `selenium` (webdriver, By, Options, WebDriverWait, EC)
- `pytesseract` (OCR for captcha solving)
- `PIL` (Image processing)
- `pandas` (Data organization)
- `os`, `time`, `glob` (File operations)

**Process:**
1. Configure Chrome browser options for PDF downloading
2. Set download directory path
3. Initialize WebDriver with custom preferences
4. Define reference IDs to process

### Step 2: Browser Automation
**Process:**
1. Opens Chrome browser in headless mode
2. Navigates to GEM contract page: `https://gem.gov.in/view_contracts/bid_detail?bid_no=REFERENCE_ID`
3. Checks for valid tender results ("No Result Found" handling)
4. Clicks contract number element to trigger captcha

### Step 3: Captcha Handling
**Libraries Used:**
- `pytesseract` (OCR)
- `base64` (Image decoding)
- `PIL.Image` (Image processing)

**Process:**
1. Locates captcha image element
2. Extracts base64 encoded image data
3. Converts to PIL Image object
4. Uses Tesseract OCR to extract text
5. Enters solved captcha in input field
6. Handles refresh if captcha fails (up to 8 attempts)

### Step 4: PDF Download and Management
**Process:**
1. After successful captcha submission:
   - Waits for download button to appear
   - Clicks download button
   - Monitors download directory for completion
2. Tracks downloaded files with metadata:
   - Reference ID
   - PDF filename
   - Download timestamp
   - File path
3. Handles failed downloads with appropriate status

### Step 5: Reporting and Output
**Libraries Used:**
- `pandas` (DataFrame creation)
- `glob` (File searching)

**Process:**
1. Compiles all download attempts into a DataFrame
2. Generates CSV report with columns:
   - reference_id
   - pdf_name
   - pdf_path
   - status (success/failed)
3. Saves report as `download_results.csv`

## Sample CSV Output Structure

```csv
reference_id	pdf_name	pdf_path
0	GEM/2024/B/5588836	no result found	no result found
1	GEM/2025/B/6071338	GEMC-511687710659558-12042025 (1).pdf	use_yourown_path\gempdf\GEMC-511687710659558-12042025 (1).pdf
2	GEM/2024/B/5594165	GEMC-511687755678653-28112024 (1).pdf	use_yourown_path\gempdf\GEMC-511687755678653-28112024 (1).pdf
3	GEM/2024/B/5458607	GEMC-511687797936727-19122024 (1).pdf	use_yourown_path\gempdf\GEMC-511687797936727-19122024 (1).pdf
4	GEM/2024/B/5480361	GEMC-511687753705287-01012025 (1).pdf	use_yourown_path\gempdf\GEMC-511687753705287-01012025 (1).pdf
5	GEM/2024/B/4560359	GEMC-511687772753116-22102024 (1).pdf	use_yourown_path\gempdf\GEMC-511687772753116-22102024 (1).pdf
6	GEM/2018/B/119037	no result found	no result found
7	GEM/2022/B/1919736	GEMC-511687766920434-25022022 (1).pdf	use_yourown_path\gempdf\GEMC-511687766920434-25022022 (1).pdf
8	GEM/2024/B/5598504	GEMC-511687718974362-08012025 (1).pdf	use_yourown_path\gempdf\GEMC-511687718974362-08012025 (1).pdf

