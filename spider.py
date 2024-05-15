import threading
from queue import Queue, Empty
from urllib.request import urlopen
from web_parser import WebParser, normalize_url, get_domain_name

# Shared resources across all Spider threads
url_queue = Queue()  # Queue of URLs to crawl
crawled_urls = set()  # Set of URLs that have been crawled
crawled_lock = threading.Lock()  # Lock to synchronize access to crawled_urls


class Spider(threading.Thread):
    """ Spider class is responsible for crawling URLs and extracting links from the page content."""

    def __init__(self, base_url):
        super().__init__()
        self.daemon = True  # Exit when the main thread exits
        self.base_url = base_url
        url_queue.put(self.base_url)  # Start with the base URL

    def run(self):
        """ the job method of threads to start crawling URLs."""
        while True:
            try:
                current_url = url_queue.get(timeout=5)  # Wait for a URL for up to 5 seconds
                self.process_url(current_url)
                url_queue.task_done()
            except Empty:
                print(f"{self.name} timed out waiting for URLs, exiting...")
                break

    def process_url(self, url):
        """Process a URL by crawling the page content and extracting links."""
        normalized_url = normalize_url(url)
        base_domain = get_domain_name(self.base_url)
        current_domain = get_domain_name(normalized_url)

        if current_domain != base_domain:
            return  # Skip URLs that are not part of the base domain to avoid crawling the whole internet

        with crawled_lock:
            if normalized_url in crawled_urls:
                return
            crawled_urls.add(normalized_url)

        print(f"Spider {self.name} crawling: {normalized_url}")
        try:
            response = urlopen(normalized_url)  # Open the URL
            content = response.read().decode('utf-8')  # Read the content of the page
            links = self.extract_links(content, normalized_url)  # Extract links from the page content
            for url in links:
                if get_domain_name(url) == base_domain:  # Only add links from the same domain
                    normalized_link = normalize_url(url)
                    with crawled_lock:
                        if normalized_link not in crawled_urls:
                            url_queue.put(normalized_link)
        except Exception as e:
            print(f"Error crawling {normalized_url}: {e}")

    @staticmethod
    def extract_links(html_content, base_url):
        """Extract all hyperlinks from the HTML content of a web page."""
        parser = WebParser(base_url)
        parser.feed(html_content)
        return parser.page_links()
