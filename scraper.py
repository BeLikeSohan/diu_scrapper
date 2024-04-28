import logging
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urlparse
import json
import os
from bs4 import BeautifulSoup
import warnings
from bs4 import GuessedAtParserWarning

logging.getLogger('scrapy').propagate = False
warnings.filterwarnings('ignore', category=GuessedAtParserWarning)

class WebsiteScraper(CrawlSpider):
    name = 'website_scraper'
    allowed_domains = ['daffodilvarsity.edu.bd']
    start_urls = ['https://daffodilvarsity.edu.bd']
    deny_domains = ['forum.daffodilvarsity.edu.bd', 'opac.daffodilvarsity.edu.bd', 'koha.daffodilvarsity.edu.bd',
                    'www.pinterest.com', 'api.whatsapp.com', 'elearn.daffodilvarsity.edu.bd']
    rules = (
        Rule(LinkExtractor(allow=allowed_domains, deny=deny_domains), callback='parse_page', follow=True),
    )

    def __init__(self, *args, **kwargs):
        super(WebsiteScraper, self).__init__(*args, **kwargs)
        self.file_count = 1
        self.url_mapping = {}
        os.makedirs('dump', exist_ok=True)

    def parse_page(self, response):
        for url in self.deny_domains:
            if url in response.url:
                return;
        print(f"Scraping: {response.url}")
        url = response.url
        content_type = response.headers.get('Content-Type', '').decode('ascii')
        if 'application/pdf' in content_type:
            self.save_pdf(url, response.body)
        else:
            soup = BeautifulSoup(response.text)
            text_content = soup.get_text()
            self.save_to_file(url, text_content)

    def save_to_file(self, url, text_content):
        filename = f"dump/file_{self.file_count}.txt"
        self.url_mapping[filename] = url
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(text_content)
        self.save_mapping_json()
        self.file_count += 1

    def save_pdf(self, url, pdf_content):
        filename = f"dump/file_{self.file_count}.pdf"
        self.url_mapping[filename] = url
        with open(filename, 'wb') as file:
            file.write(pdf_content)
        self.save_mapping_json()
        self.file_count += 1

    def save_mapping_json(self):
        with open('dump/url_mapping.json', 'w', encoding='utf-8') as file:
            json.dump(self.url_mapping, file, ensure_ascii=False, indent=4)

    def _url_for_allowed_domain(self, url):
        domain = urlparse(url).netloc
        return domain.endswith('.daffodilvarsity.edu.bd')

    def close(self, reason):
        super().close(self, reason)