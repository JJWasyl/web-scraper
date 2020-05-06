from scraper import search_and_download_opera

if __name__ == "__main__":
    search_term = "Dogs"
    exec_path = r"C:\Users\jjwas\AppData\Local\Programs\Opera\68.0.3618.63\opera.exe"
    search_and_download_opera(search_term, exec_path, r"./experiments", 10)
