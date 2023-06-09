"""
Takes in a string and search that string(case insensitive) inside the webpages if found a match then returns the link for it
"""
import sys
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

int_links=0
ext_links=0
visited_links = set()
internal_links = set()
external_links = set()

def crawl(url, start_domain, search_string, depth=1, max_depth=None):
    """
    Crawls the given URL and extracts links from the page.
    Recursively follows the links within the same domain up to the maximum depth threshold.
    Searches for the specified string within the page content.
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

    soup = BeautifulSoup(response.text, "lxml")
    links = soup.find_all(["a", "img", "link", "script","iframe","form"])

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
       
        if "action" in link.attrs :
            action = link["action"]
            if action.startswith("http") :
                next_url = action
            else :
                next_url = urljoin(url, action)
            process_url(next_url, start_domain, depth+1, max_depth)
            
def process_url(url, start_domain, search_string, depth=1, max_depth=None):
    """
    Processes the URL and determines whether to crawl or consider it as an internal or external link.
    Searches for the specified string within the page content.
    """
    global int_links 
    global ext_links
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if domain == start_domain:
        if url not in visited_links:
            if max_depth is None or depth <= max_depth:
                int_links+=1
                internal_links.add(url)
                crawl(url, start_domain, search_string, depth, max_depth)
    else:
        if url not in external_links :
            ext_links+=1
            external_links.add(url)

def search_string_in_page(url, search_string):
    """
    Fetches the HTML content of the page at the specified URL and searches for the string within the content.
    Returns True if the string is found, False otherwise.
    """

    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        return False

    if response.status_code != 200:
        return False

    page_text = response.text
    return search_string.lower() in page_text.lower() # It does case insensitive searching

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
    print(f"\nTotal Internal Links = {int_links} \n")

    print("\nExternal links:")
    for link in external_links:
        print(link)
    print(f"\nTotal External Links = {ext_links} \n")
    if search_string:
        print("\nSearch results:")
        found = False
        for link in internal_links:
            if search_string_in_page(link, search_string):
                found = True
                print(f"Search result in Internal Link: {link}")
        if not found:
            print("\nNo Internal link found with the search string.\n")
        found=False
        for link in external_links :
            if search_string_in_page(link,search_string) :
                found=True
                print(f"Search result in External Link: {link}")
        if not found :
            print("\nNo External link with the search string.\n")
