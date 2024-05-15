import threading
import time
from queue import Queue
from spider import Spider, crawled_urls
from web_parser import get_domain_name, is_valid_url, normalize_url
from local_storage import *

#
# # Number of spider threads to run concurrently
# BASE_URL = "https://webscraper.io/test-sites/e-commerce/allinone"
PROJECT_NAME = 'MyWebCrawler'
NUMBER_OF_THREADS = 8  # depends on the number of cores in your CPU
init_lock = threading.Lock()


# threads_queue = Queue()
# waiting = set()
# crawled = set()


def main():
    with init_lock:
        base_url = input("Enter the URL to start crawling: ")
        if not is_valid_url(base_url):
            print("Invalid URL. Exiting...")
            return

    spiders = [Spider(base_url) for _ in range(NUMBER_OF_THREADS)]
    for spider in spiders:
        spider.start()
    for spider in spiders:
        spider.join()

    print("Crawling has completed.")
    print("Saving data to files...")

    create_data_files(base_url)
    set_to_file(crawled_urls, os.path.join('crawled.txt'))


if __name__ == "__main__":
    main()
