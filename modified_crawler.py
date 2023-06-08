"""
This code takes in a string and search it in the links not within the webpages that open after following the link it 
also seperates the internal and external links
"""
import sys
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

visited_links = set()
internal_links = set()
external_links = set()
found_links = False

def crawl(url, start_domain, search_string, depth=1, max_depth=None):
    """
    Crawls the given URL and extracts links from the page.
    Recursively follows the links within the same domain up to the maximum depth threshold.
    Prints the links that contain the specified search string.
    """

    visited_links.add(url)
    print("Crawling:", url)

    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        return

    if response.status_code != 200:
        print("Failed to crawl:", url)
        return

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all(["a", "img", "link", "script"])

    for link in links:
        if "href" in link.attrs:
            href = link["href"]
            if href.startswith("http"):
                next_url = href
            else:
                next_url = urljoin(url, href)
            process_url(next_url, start_domain, search_string, depth + 1, max_depth)
        
        if "src" in link.attrs:
            src = link["src"]
            if src.startswith("http"):
                next_url = src
            else:
                next_url = urljoin(url, src)
            process_url(next_url, start_domain, search_string, depth + 1, max_depth)

def process_url(url, start_domain, search_string, depth=1, max_depth=None):
    """
    Processes the URL and determines whether to crawl or consider it as an internal or external link.
    """

    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if domain == start_domain:
        if url not in visited_links:
            if max_depth is None or depth <= max_depth:
                internal_links.add(url)
                crawl(url, start_domain, search_string, depth, max_depth)
    else:
        external_links.add(url)

        if search_string and search_string in url:
            global found_links
            found_links = True
            print("Link with search string:", url)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web Crawler")
    parser.add_argument("-u", "--url", help="Start URL", required=True)
    parser.add_argument("-t", "--threshold", help="Recursion Depth Threshold", type=int, default=None)
    parser.add_argument("-s", "--search", help="Search String", default="")
    args = parser.parse_args()

    start_url = args.url
    threshold = args.threshold
    search_string = args.search

    parsed_start_url = urlparse(start_url)
    start_domain = parsed_start_url.netloc

    if threshold is None:
        crawl(start_url, start_domain, search_string)
    else:
        crawl(start_url, start_domain, search_string, max_depth=threshold)

    print("\nInternal links:")
    for link in internal_links:
        print(link)

    print("\nExternal links:")
    for link in external_links:
        print(link)

    if search_string and not found_links:
        print("\n No links found with the search string:")
