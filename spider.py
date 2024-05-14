from urllib.request import urlopen
from web_parser import WebParser, normalize_url
from local_storage import *


class Spider:
    # Class variables (shared among all instances)
    project_name = "this_crawler"
    base_url = ''
    domain_name = ''
    waiting_file = ''
    crawled_file = ''
    waiting_queue = set()
    crawled = set()

    # Initialize the Spider, We use multiple spiders to crawl multiple websites simultaneously
    def __init__(self, project_name, base_url, domain_name):
        Spider.project_name = project_name
        Spider.base_url = base_url
        Spider.domain_name = domain_name
        Spider.waiting_file = Spider.project_name + '/waiting.txt'
        Spider.crawled_file = Spider.project_name + '/crawled.txt'
        self.boot()  # Initialize the Spider
        self.crawl_page('First spider', Spider.base_url)  # Start crawling the first page

    # Create directory and files for the project on first run and start the Spider
    @staticmethod
    def boot():
        """Initialize the Spider and create the project directory and files if not created"""
        create_project_dir(Spider.project_name)
        create_data_files(Spider.project_name, Spider.base_url)
        Spider.waiting_queue = file_to_set(Spider.waiting_file)
        Spider.crawled = file_to_set(Spider.crawled_file)

    @staticmethod
    def crawl_page(thread_name, page_url):
        """Crawl the page and add the links to the waiting queue"""
        normalized_url = normalize_url(page_url)
        if normalized_url not in Spider.crawled:
            print(thread_name + ' now crawling ' + normalized_url)
            print('Waiting ' + str(len(Spider.waiting_queue)) + ' | Crawled ' + str(len(Spider.crawled)))
            Spider.add_links_to_waiting(Spider.gather_links(normalized_url))
            if normalized_url in Spider.waiting_queue:
                Spider.waiting_queue.remove(normalized_url)
            Spider.crawled.add(normalized_url)
            Spider.update_files()

    @staticmethod
    def gather_links(normalized_url):
        """Extract the links from the page and return them as a set
        NOTE - only crawl_page calls this function that pages are already normalized
        :param normalized_url: The already normalized URL of the page to extract the links
        :return: A set of links extracted from the page
        """
        html_string = ''
        try:
            response = urlopen(normalized_url)  # Open the url in bytes format
            if 'text/html' in response.getheader('Content-Type'):
                html_bytes = response.read()  # Read the bytes of the page
                html_string = html_bytes.decode('utf-8')  # Convert the bytes to string
            web_parser = WebParser(Spider.base_url, normalized_url)  # Create an instance of the LinkExtractor class
            web_parser.feed(html_string)  # Feed the HTML string to the LinkExtractor
        except Exception as e:
            print("Error: can't crawl page " + normalized_url + '\n' + str(e))
            return set()  # Return an empty set of links if an error occurred
        # ELSE return the set of links extracted from the page
        return web_parser.page_links()

    @staticmethod
    def add_links_to_waiting(links):
        """Add the links to the waiting queue"""
        for url in links:
            if url in Spider.waiting_queue or url in Spider.crawled:
                # Handle duplicates - We have already crawled this page or it is in the queue to be crawled
                continue
            if Spider.domain_name not in url:
                # We are not interested in external links only ones that belong to the domain
                continue
            Spider.waiting_queue.add(url)

    @staticmethod
    def update_files():
        """Update the files with the new data"""
        set_to_file(Spider.waiting_queue, Spider.waiting_file)
        set_to_file(Spider.crawled, Spider.crawled_file)
