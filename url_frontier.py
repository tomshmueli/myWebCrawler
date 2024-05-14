import threading
import time
from queue import Queue
from spider import Spider
from web_parser import get_domain_name, is_valid_url, normalize_url
from local_storage import *

# Number of spider threads to run concurrently
NUMBER_OF_SPIDERS = 1  # depends on the number of cores in your CPU
WAITING_FILE = 'waiting.txt'
CRAWLED_FILE = 'crawled.txt'
PROJECT_NAME = 'MyWebCrawler'
init_lock = threading.Lock()
threads_queue = Queue()


def create_threads():
    """Create threads that will process the URLs in the queue."""
    for _ in range(NUMBER_OF_SPIDERS):
        t = threading.Thread(target=job, daemon=True)
        t.start()


def job():
    """Function to be run by each thread. This fetches a URL from the queue and starts the crawling process."""
    while True:
        url = threads_queue.get()
        Spider.crawl_page(threading.current_thread().name, url)
        threads_queue.task_done()


def create_jobs():
    """Read the queue file and add URLs to the queue."""
    waiting_urls = file_to_set(WAITING_FILE)
    for url in waiting_urls:
        threads_queue.put(url)
    threads_queue.join()
    crawl()


def crawl():
    """Check if there are items in the queue, if so, crawl them."""
    queued_links = file_to_set(WAITING_FILE)
    if len(queued_links) > 0:
        print(f"{len(queued_links)} links in the queue")
        create_jobs()


def main():
    """Main function to start the crawler."""
    with init_lock:  # critical section for initializing the project and first spider
        seed_url = input("Enter the seed URL to start crawling: ")  # Get seed URL from the user
        if is_valid_url(seed_url):
            seed_url = normalize_url(seed_url) # Normalize the URL
        Spider(PROJECT_NAME, seed_url, get_domain_name(seed_url))

    # release the lock and start the threads
    create_threads()
    crawl()


if __name__ == "__main__":
    main()
