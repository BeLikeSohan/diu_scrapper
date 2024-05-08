import requests
import urllib3
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import os
import re

# Disable SSL certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set the starting URL
start_url = "https://www.daffodilvarsity.edu.bd"

# Subdomains to skip
skip_subdomains = ["forum.daffodilvarsity.edu.bd", "dspace.daffodilvarsity.edu.bd"]

# Create a directory to store the text files
output_dir = "website_files"
os.makedirs(output_dir, exist_ok=True)

# Create a set to store visited URLs
visited_urls = set()

# Define a function to crawl a URL
def crawl(url):
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        save_text(url, soup.get_text())
        visited_urls.add(url)
        print(f"Downloaded: {url}")

        # Find all links on the page
        for link in soup.find_all("a"):
            href = link.get("href")
            if href:
                parsed_url = urlparse(href)
                if not parsed_url.scheme:
                    # Relative URL, join with base URL
                    href = urljoin(url, href)
                if url_belongs_to_domain(href, start_url) and href not in visited_urls and parsed_url.netloc not in skip_subdomains:
                    crawl(href)

    except requests.exceptions.RequestException as e:
        print(f"Error crawling {url}: {e}")

# Define a function to check if a URL belongs to the target domain
def url_belongs_to_domain(url, start_url):
    parsed_url = urlparse(url)
    parsed_start_url = urlparse(start_url)
    return parsed_url.netloc.endswith(parsed_start_url.netloc)

# Define a function to sanitize the URL for use as a file name
def sanitize_url(url):
    # Remove protocol and trailing slash
    sanitized = re.sub(r'^(https?://)?(www\.)?', '', url.strip('/'))
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', sanitized)
    return sanitized

# Define a function to save the text content
def save_text(url, text):
    filename = os.path.join(output_dir, f"{sanitize_url(url)}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

# Start the crawling process
crawl(start_url)