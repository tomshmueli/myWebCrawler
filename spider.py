import threading
from queue import Queue, Empty
from urllib.request import urlopen
from web_parser import WebParser, normalize_url, get_domain_name
import tldextract

# Shared resources across all Spider threads
url_queue = Queue()
crawled_urls = set()
crawled_lock = threading.Lock()


class Spider(threading.Thread):
    def __init__(self, base_url):
        super().__init__()
        self.daemon = True  # Exit when the main thread exits
        self.base_url = base_url
        url_queue.put(self.base_url)  # Start with the base URL

    def run(self):
        while True:
            try:
                current_url = url_queue.get(timeout=5)  # Wait for a URL for up to 5 seconds
                self.process_url(current_url)
                url_queue.task_done()
            except Empty:
                print(f"{self.name} timed out waiting for URLs, exiting...")
                break

    def process_url(self, url):
        normalized_url = normalize_url(url)
        base_domain = get_domain_name(self.base_url)
        current_domain = get_domain_name(normalized_url)

        if current_domain != base_domain:
            return  # Skip URLs that are not part of the base domain

        with crawled_lock:
            if normalized_url in crawled_urls:
                return
            crawled_urls.add(normalized_url)

        print(f"Spider {self.name} crawling: {normalized_url}")
        try:
            response = urlopen(normalized_url)
            content = response.read().decode('utf-8')
            links = self.extract_links(content, normalized_url)
            for url in links:
                if get_domain_name(url) == base_domain:
                    normalized_link = normalize_url(url)
                    with crawled_lock:
                        if normalized_link not in crawled_urls:
                            url_queue.put(normalized_link)
        except Exception as e:
            print(f"Error crawling {normalized_url}: {e}")

    @staticmethod
    def extract_links(html_content, base_url):
        parser = WebParser(base_url)
        parser.feed(html_content)
        return parser.page_links()
