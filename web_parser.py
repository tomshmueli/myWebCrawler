from html.parser import HTMLParser
from urllib import parse
import re
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from urllib.request import urlopen

import requests


class WebParser(HTMLParser):
    """
    WebParser class is responsible for parsing HTML content of a specific web page and extracting
    all hyperlinks from that page
    """

    def __init__(self, page_url, page_counter=0):
        super().__init__()
        self.page_url = page_url  # Unique URL of the page we are crawling
        self.page_count = page_counter  # Amount of times we were requested to crawl a page
        self.links = set()  # Set of links found to crawl

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (attribute, value) in attrs:
                if attribute == 'href':
                    url = parse.urljoin(self.page_url, value)
                    self.links.add(url)

    def page_links(self):
        return self.links

    def error(self, message):
        print(message)


def get_domain_name(url):
    """
    Get the domain name from a given URL
    (e.g., 'https://www.example.com:8080/path?query=abc' -> 'example.com').
    If the URL does not include a scheme, 'http://' will be prepended.

    args--> url (str): The URL from which to extract the domain name.
    $ret--> (str): The domain name of the URL.
    """
    try:
        # Ensure URL has a scheme for proper parsing
        if not urlparse(url).scheme:
            url = 'http://' + url
        sub_domain = urlparse(url).netloc
    except Exception as e:
        print("Error: can't parse the URL", e)
        return ""

    # Remove port number if present
    sub_domain = sub_domain.split(':')[0]

    # Break the domain into parts and try to extract the second level domain and TLD
    parts = sub_domain.split('.')
    if len(parts) > 1:
        domain = parts[-2] + '.' + parts[-1]
    else:
        # If there's no dot or only one part, return as is
        domain = sub_domain

    return domain


def normalize_url(url):
    """
    Normalize a URL by standardizing the scheme, removing 'www.', lowercasing the path,
    sorting and selectively including query parameters, and ignoring the fragment.
    """
    parsed = urlparse(url)

    # Standardize the scheme
    scheme = 'https' if parsed.scheme in ['http', 'https'] else parsed.scheme

    # Lowercase the hostname and remove 'www.'
    netloc = parsed.netloc.lower()
    if netloc.startswith('www.'):
        netloc = netloc[4:]

    # Lowercase the path
    path = parsed.path.lower()
    if path.endswith('/') and len(path) > 1:
        path = path.rstrip('/')

    # Handle query parameters selectively
    query = parse_qs(parsed.query)
    # Exclude known tracking parameters or irrelevant ones
    filtered_query = {k: v for k, v in query.items() if not k.startswith("utm_")}
    sorted_query = sorted((k.lower(), v[0].lower()) for k, v in filtered_query.items())
    query_string = urlencode(sorted_query, doseq=True)

    # Reconstruct the normalized URL without the fragment
    normalized = urlunparse((scheme, netloc, path, None, query_string, None))

    return normalized


def is_valid_url(url):
    """Check if the given URL is valid and verify it resolves online."""
    # Check if URL has a scheme, if not prepend one for validation purposes
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "http://" + url  # Assume http if no scheme is provided
        parsed = urlparse(url)

    # Regex to validate the URL structure
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:www\.)?'  # optional www
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'  # domain...
        r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain extension
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    # Verify structure
    if not re.match(regex, url):
        return False

    # Attempt to access the URL to check if it's active and reachable
    try:
        response = requests.head(url, timeout=3)
        return response.status_code == 200
    except requests.RequestException:
        return False


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
        web_parser = WebParser(normalized_url)  # Create an instance of the LinkExtractor class
        web_parser.feed(html_string)  # Feed the HTML string to the LinkExtractor
    except Exception as e:
        print("Error: can't crawl page " + normalized_url + '\n' + str(e))
        return set()  # Return an empty set of links if an error occurred
    # ELSE return the set of links extracted from the page
    return web_parser.page_links()
