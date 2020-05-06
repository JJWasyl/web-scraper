from selenium import webdriver
import time
import requests
from PIL import Image
import io
import os
import hashlib


class GoogleImagesScraper:
    """
    A simple scraper for google images search
    """
    def __init__(self, web_driver: webdriver = None, instruction_sleep=1):
        """
        :param web_driver: selenium.webdriver object for driving the browser
        :param instruction_sleep: time offset between instructions
        """
        if web_driver is None:
            raise ValueError("Error, webdriver object needed")
        else:
            self.wd = web_driver
        self.sleep_between_interactions = instruction_sleep

    def scroll_to_end(self):
        """
        Fully scrolls a google images site
        """
        self.wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(self.sleep_between_interactions)

    def fetch_image_urls(self, query: str, max_links: int):
        """
        Collects urls of images matching selected query
        :param query: (str) Selected query that you would input into a search box
        :param max_links: (int) maximum amount of image links to collect at once
        :return image_urls: (list) returns a list of found image links for download
        """
        # search query, q will be formatted to the query
        search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

        # page loading
        self.wd.get(search_url.format(q=query))

        image_urls = set()
        image_count = 0
        results_start = 0

        while image_count < max_links:
            self.scroll_to_end()

            #thumbnails
            thumbnail_results = self.wd.find_elements_by_css_selector("img.rg_i.Q4LuWd.tx8vtf")
            number_results = len(thumbnail_results)
            print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")

            for img in thumbnail_results[results_start:number_results]:
                # trying to click each thumbnail
                try:
                    img.click()
                    time.sleep(self.sleep_between_interactions)
                except Exception:
                    continue

                # extract image urls
                actual_images = self.wd.find_elements_by_css_selector("img.n3VNCb")
                for actual_image in actual_images:
                    if actual_image.get_attribute("src") and "http" in actual_image.get_attribute("src"):
                        image_urls.add(actual_image.get_attribute("src"))

                image_count = len(image_urls)

                if image_count >= max_links:
                    print(f"Found: {len(image_urls)} image links, done!")
                    break
                else:
                    print("Found:", len(image_urls), "image links, looking for more ...")
                    time.sleep(1)
                    load_more_button = self.wd.find_elements_by_css_selector(".ksb")
                    if load_more_button:
                        self.wd.execute_script("document.querySelector('.ksb').click();")

                results_start = len(thumbnail_results)

        return image_urls

    @staticmethod
    def download_image(folder_path: str, url: str, max_tries=2):
        """
        Donwloads selected image from given url into a folder of yoru chosing
        :param folder_path: (str) Desired target folder
        :param url: (str) target image url
        """
        image_content = None
        for i in range(max_tries):
            try:
                image_content = requests.get(url).content
            except Exception as e:
                print(f"ERROR - Could not download {url} try {i+1}/{max_tries} - {e}")
                if i+1 < max_tries:
                    time.sleep(5)
                continue
            break

        try:
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file).convert("RGB")
            file_path = os.path.join(folder_path, hashlib.sha1(image_content).hexdigest()[:10] + ".jpg")
            with open(file_path, "wb") as f:
                image.save(f, "JPEG", quality=85)
            print(f"SUCCESS - saved {url} - as {file_path}")
        except Exception as e:
            print(f"ERROR - Could not save {url} - {e}")


def search_and_download_opera(search_term: str, executable_path: str, target_path: str = './images',
                              image_number: int = 5):
    """
    Wrapper function for the Opera browser
    :param search_term: (str) Term to search images for
    :param executable_path: (str) Path to the Opera executable (opera.exe)
    :param target_path: (str) target folder path for images
    :param image_number: (int) how many images to download
    """
    target_folder = os.path.join(target_path, '_'.join(search_term.lower().split(' ')))
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    options = webdriver.ChromeOptions()
    options.binary_location = executable_path
    with webdriver.Opera(options=options) as driver:
        scraper = GoogleImagesScraper(driver)
        res = scraper.fetch_image_urls(search_term, image_number)

    for elem in res:
        scraper.download_image(target_folder, elem)

    driver.quit()


if __name__ == "__main__":
    search_term = "Dariusz Wasylkowski"
    exec_path = r"C:\Users\jjwas\AppData\Local\Programs\Opera\68.0.3618.63\opera.exe"
    search_and_download_opera(search_term, exec_path, r"./experiments", 5)
