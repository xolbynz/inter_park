# README

---

## Prerequisites

### Required Tools
- **Python** (>=3.7)
- **Google Chrome** browser
- **ChromeDriver** compatible with your Chrome browser version

### Python Libraries
Install the required libraries using:
```bash
pip install selenium
```

### Windows Users
If you are using Windows and need OCR functionality, install Tesseract from the following path:
```
C:\Program Files\Tesseract-OCR\tesseract.exe
```

---



```
Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" -ArgumentList "--remote-debugging-port=9222", "--user-data-dir=C:\chrome_tmp"
```
