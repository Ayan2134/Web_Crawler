import sys
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
"""
should not use {} to initilize empty set here as it may cause confusion with empty dict as well ,better to implicitly 
define it as a set using set() . Used set here to avoid repeating links in recursion as it will become an infinte loop otherwise
"""
visited_links = set() #to store already visited links 
internal_links = set() #to group internal links which will be crawled further
external_links = set() #to store external links(links with same domain) which will just be mentioned and not crawled 
def crawl(url, start_domain, depth, max_depth):
    if max_depth != None :
        if depth>max_depth :
            return
    """
    Crawls the given URL and extracts links from the page.
    Recursively follows the links within the same domain up to the maximum depth threshold.
    """

    visited_links.add(url)
    print("Crawling:", url)

    try:
        response = requests.get(url) #on succesful request response.status_code is set to 200
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        return

    if response.status_code != 200:
        print("Failed to crawl:", url)
        return
    """
    #reponse.text is a str containing html or xml test of the url we can also use response.content which returns the html
    or xml doc in bytes format which can be converted to str using response.content.decode() . As for 2nd argument we can use 
    "html.parser" or "lxml" html.parser is linenent and can convert even imperfect or malfunctioned html but lxml has more features 
    and it is also faster. Hence, it is recommended for html and xml docs
    """
    soup = BeautifulSoup(response.text, "lxml") 
    links = soup.find_all(["a", "img", "link", "script", "iframe", "form"]) 

    for link in links:
        if "href" in link.attrs:
            href = link["href"]
            if href.startswith("http"):
                next_url = href
            else :
                next_url = urljoin(url, href) #to manage relative url (makes relative url absolute)
                """
                urljoin is used instead of simply concatenating the strings because if the url has already some relative part attached
                to it then it removes that and attach the relative url provided by user as argument and returns it as a proper url
                """
            process_url(next_url, start_domain, depth , max_depth)
        
        if "src" in link.attrs:
            src = link["src"]
            if src.startswith("http"):
                next_url = src
            else:
                next_url = urljoin(url, src)
            process_url(next_url, start_domain, depth , max_depth)
        
        if "action" in link.attrs :
            action = link["action"]
            if action.startswith("http") :
                next_url = action
            else :
                next_url = urljoin(url, action)
            process_url(next_url, start_domain, depth, max_depth)

def process_url(url, start_domain, depth, max_depth):
    """
    Processes the URL and determines whether to crawl or consider it as an internal or external link.
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if domain == start_domain:
        if url not in visited_links:
            if max_depth is None or depth <= max_depth:
                internal_links.add(url)
                crawl(url, start_domain, depth+1, max_depth)
    else:
        if url not in external_links : #to count only unique external links although it doesn't matter as it is a set
            external_links.add(url)
    
def search_string_source_code(url, search_string):
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
    parser.add_argument("-o","--output", help="Create an output file ", default="")
    args = parser.parse_args()
    start_url = args.url
    threshold = args.threshold
    output_file=args.output
    search_string = args.search
    parsed_start_url = urlparse(start_url)
    start_domain = parsed_start_url.netloc
    if threshold is None or threshold>0 :
        if output_file :
            if os.path.exists(output_file) :
                print("\nThis file already exists in the current directory..... Printing output on the command line\n\n")
            else :
                path=f"./{output_file}"
                sys.stdout=open(path,"w")
        crawl(start_url, start_domain, 1,threshold)
        print("\nInternal links:")
        for link in internal_links:
            print(link)
        print(f"\nTotal Internal Links = {len(internal_links)} \n")
        print("\nExternal links:")
        for link in external_links:
            print(link)
        print(f"\nTotal External Links = {len(external_links)} \n")
        if search_string:
            print("\nSearch results:")
            found = False
            for link in internal_links:
                if search_string_source_code(link, search_string):
                    found = True
                    print(f"Search result in Internal Link: {link}")
            if not found:
                print("\nNo Internal link found with the search string.\n")
            found=False
            for link in external_links :
                if search_string_source_code(link,search_string) :
                    found=True
                    print(f"Search result in External Link: {link}")
            if not found :
                print("\nNo External link with the search string.\n")

    else :
        print("Invalid Threshhold")