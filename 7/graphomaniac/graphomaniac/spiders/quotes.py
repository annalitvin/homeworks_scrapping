import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com/"]

    max_count_follow = 1

    custom_settings = {"DOWNLOAD_DELAY": 2}

    def parse(self, response):
        quote_rows = response.xpath('.//div[@class="row"]//div[@class="quote"]')

        for row in quote_rows:
            text = row.xpath('.//span[@class="text"]/text()').get().strip("“”")
            author_name = row.xpath('.//small[@class="author"]/text()').get()

            yield {"text": text, "author": author_name}

        next_btn = response.xpath('//li[@class="next"]/a/@href').get()
        if next_btn and self.max_count_follow:
            self.max_count_follow -= 1
            yield response.follow(next_btn, callback=self.parse)
