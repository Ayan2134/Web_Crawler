#internal and external links are saved in sets so no repetition
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
       external_links.add(url)

def group_domain() :  
    domain=set()  
    for link in external_links :
        parsed_url=urlparse(link)
        if parsed_url.netloc:
            domain.add(parsed_url.netloc)
    for domain_name in domain :
        print(f"\n{domain_name}\n")
        for link in external_links :
            parsed_url=urlparse(link)
            if domain_name==parsed_url.netloc :
                print("\t",link)

def sort_extensions(links) :
    extension=set()
    for link in links:    
        parsed_link = urlparse(link)
        path = parsed_link.path
        extension.add(os.path.splitext(path)[1])
    for ext in extension:
        if ext!="":
            print(f"\n{ext}\n")
        else :
            print("\nMiscellaneous\n")
        for link in links :
            parsed = urlparse(link)
            link_path = parsed.path
            link_ext=os.path.splitext(link_path)[1]
            if link_ext==ext :
                print("\t",link)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web Crawler")
    parser.add_argument("-u", "--url", help="Start URL", required=True)
    parser.add_argument("-t", "--threshold", help="Recursion Depth Threshold", type=int, default=None)
    parser.add_argument("-o","--output", help="Create an output file ", default="")
    parser.add_argument("-s","--simple",help="Simplify the results that we get",action="store_true")
    parser.add_argument("-e","--ext_sort",help="Sort the external links based on extensioin",action="store_true")
    args = parser.parse_args()
    start_url = args.url
    threshold = args.threshold
    output_file=args.output
    simple=args.simple 
    ext_sort=args.ext_sort
    parsed_start_url = urlparse(start_url)
    start_domain = parsed_start_url.netloc
    flag=False #to check if output file was made or not
    if threshold is None or threshold>0 :
        if output_file :
            if os.path.exists(output_file) :
                print("\nThis file already exists in the current directory..... Printing output on the command line\n\n")
            else :
                path=f"./{output_file}"
                sys.stdout=open(path,"w")
                flag=True
        crawl(start_url, start_domain, 1,threshold)
        print("\nInternal links:\n")
        if simple==True : #getting simplified output
            for link in internal_links:
                print("\t",link)
        else :
            sort_extensions(internal_links)
        print(f"\nTotal Internal Links = {len(internal_links)} \n")
        print("\nExternal links:")
        if simple==True : #getting simplified output
            for link in external_links :
                print("\t",link)
        else :
            group_domain()
        if ext_sort==True :
            print("\nExternal links sorted based on extensions :\n")
            sort_extensions(external_links)
        print(f"\nTotal External Links = {len(external_links)} \n")
        print(f"\nTotal Links = {len(internal_links)+len(external_links)} \n")
        if flag :
            sys.stdout=sys.__stdout__ #restoring sys,stdout to its original state, sys.__stdout__ refers to original output stream 
            print(f"\nTotal Internal Links Found = {len(internal_links)} \n")
            print(f"\nTotal External Links Found = {len(external_links)} \n")
            print(f"\nTotal Links Found = {len(internal_links)+len(external_links)} \n")
        
    else :
        print("Invalid Threshhold")