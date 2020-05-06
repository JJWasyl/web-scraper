# Web-Scraper
A simple web-scraping tool for collecting google images using the Opera browser.<br/>
(Adding more support as I go)

## Usage
```python
from scraper import search_and_download_opera

search_term = "Dogs"
exec_path = "path-to-opera.exe"
search_and_download_opera(search_term, exec_path, r"./experiments", 10)
```