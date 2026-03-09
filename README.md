## GEM-Tender-Document-Downloader

**Problem Statement**
ABC Ltd provides tender information services to clients across India. A recurring challenge arises when clients report that they can see tender winner bidder information on the ABC portal but cannot download the official GEM documents. Support teams then need to manually handle each tender’s reference ID, which is slow and error-prone.

- Each tender has a unique reference ID.  
- If a winner bidder name exists on GEM, the document should be downloadable as a PDF.  
- If the reference ID is invalid or GEM has not uploaded the document, this method cannot work.  

[Presentation for more details](https://drive.google.com/file/d/1f8yoK-Sas3PNsCIJRsyIhFy0Iqh2GM_T/view?usp=sharing)

---

## Manual Process (Current Challenge)
1. Visit [GEM](https://gem.gov.in/)  
2. Search each tender by reference ID  
3. Solve captchas repeatedly  
4. Download PDFs one by one  
5. Verify and send to clients  

This is manageable for 2–3 IDs but becomes overwhelming for 30–40 IDs or multiple clients at once.

---

## Automated Solution
The script enables **one-click downloading of all tender documents** using reference IDs.  
- Paste all reference IDs into a `.txt` file (comma-separated).  
- Run the code.  
- All tender documents are downloaded automatically to your chosen folder.  

👉 Use [https://delim.co/](https://delim.co/) to quickly convert reference IDs into a comma-separated format.

---

## How the Solution Works

### Step 1: Initialization
- Libraries: `selenium`, `pytesseract`, `PIL`, `pandas`, `os`, `time`, `glob`  
- Configure Chrome for PDF auto-download  
- Set download directory  
- Read reference IDs from `ref.txt`  

### Step 2: Browser Automation
- Open GEM contract page for each reference ID  
- Handle “No Result Found” cases  
- Trigger captcha challenge  

### Step 3: Captcha Handling
- Extract captcha image (base64)  
- Solve using Tesseract OCR  
- Retry up to 8 times if incorrect  

### Step 4: PDF Download
- Click download button after captcha success  
- Monitor folder until download completes  
- Record metadata: reference ID, filename, path, status  

### Step 5: Reporting
- Compile results into Excel with three columns:  
  - `reference_id`  
  - `pdf_name`  
  - `pdf_link` (clickable hyperlink)  
- Apply formatting:  
  - Column widths: 22 / 38.5 / 18  
  - Header row frozen, bold size 14  
  - Borders applied, hyperlinks styled blue and bold  

---

## Sample Excel Output
| reference_id       | pdf_name                                | pdf_link   |
|--------------------|------------------------------------------|------------|
| GEM/2024/B/5588836 | no result found                         | no result found |
| GEM/2025/B/6071338 | no result found                         | no result found |
| GEM/2024/B/5594165 | GEMC-511687755678653-28112024.pdf        | Click Here |
| GEM/2024/B/5458607 | GEMC-511687797936727-19122024.pdf        | Click Here |

---

## Limitations
- **Captcha solving**: OCR may misread text; retries increase processing time.  
- **Winner bidder availability**: If GEM has not uploaded the document, it cannot be downloaded.  
- **Reference ID validity**: Incorrect IDs will always fail.  
- **Default PDF viewer**: Hyperlinks open PDFs in your system’s default app. To use Microsoft Edge, set Edge as the default PDF viewer in Windows settings.  

---

This updated README now reflects:
- Reading reference IDs from a `.txt` file.  
- Using [delim.co](https://delim.co/) for quick formatting.  
- Excel output with hyperlinks and styling.  
- Clear limitations for users.  

Would you like me to also add a **“Quick Start” section** with exact steps (like “Step 1: Save IDs in ref.txt, Step 2: Run script, Step 3: Open Excel report”), so new users can follow without reading the whole document?
