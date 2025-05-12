# GEM-Tender-Document-Downloader


## Problem Statement
a company call 'abc ltd' is a service provider for tender information and they have clients from all over the india subscribe to thier serivices, on gem website we have tender informations
our Customer support teams handling Government e-Marketplace (GEM) portal queries face a significant challenge when clients report on call they can see tender winner information on abc ltd portal for xyz tender but cannot download the documents for that particual tender and clinet send each tender's reference id.
 - each tender has unique reference id
 - if we have winner bidder gem website must upload the whole document as a pdf

1. customer Support employee must manually:
   - Visit https://gem.gov.in/
   - Search for each tender using its unique reference ID
   - Solve captchas repeatedly for each tender
   - Download documents one-by-one
   - Verify successful downloads
   - Send documents to clients

2. This becomes time-consuming when handling clinet's on call:
   - 2-3 reference IDs (typical case)
   - 30-40 reference IDs (large cases)
   - Multiple clients simultaneously

3. Additional complications:
   - Not all customer support employee have direct database access
   - Senior agents get overloaded with more work
   - Clients remain on hold during manual verification



to solves these issues by enabling one-click downloading of all tender documents using reference IDs.
let me explain my code will give you chance to just paste your all reference ids given by client and run the code and you will get your all tender's documents in minutes

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
reference_id,pdf_name,pdf_path,status
GEM/2024/B/5588836,contract_5588836.pdf,C:\Downloads\contract_5588836.pdf,success
GEM/2025/B/6071338,no result found,N/A,failed
GEM/2024/B/5594165,contract_5594165.pdf,C:\Downloads\contract_5594165.pdf,success

