import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from amanbankkg.items import Article


class amanbankkgSpider(scrapy.Spider):
    name = 'amanbankkg'
    start_urls = ['http://www.amanbank.kg/']

    def parse(self, response):
        articles = response.xpath('//div[contains(@class, "fusion-post-large-alternate")]')
        for article in articles:
            link = article.xpath('.//h2/a/@href').get()
            date = article.xpath('.//span[@class="fusion-date"]/text()').get() + ' ' + \
                   article.xpath('.//span[@class="fusion-month-year"]/text()').get()
            if date:
                date = " ".join(date.split())

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//a[@class="pagination-next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="post-content"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
