import scrapy
from scrapy_playwright.page import PageMethod

class JobItem(scrapy.Item):
	title = scrapy.Field()
	company = scrapy.Field()
	description = scrapy.Field()
	application_link = scrapy.Field()


class SimplyHiredSpider(scrapy.Spider):
	name = "jobs"

	def start_requests(self):
		start_urls = "https://www.simplyhired.ca/search?l=toronto"
		yield scrapy.Request(start_urls, meta=dict(
                playwright = True,
                playwright_include_page = True,
								errback=self.errback, 
                playwright_page_methods =[PageMethod('wait_for_selector', 'article.SerpJob'),]
            ))
	
	BASE_URL= "https://www.simplyhired.ca"

	def parse(self, response):
		job_page_links = response.css("h3.jobposting-title a::attr(href)").getall()
		for link in job_page_links:
			absolute_url = self.BASE_URL + link
			yield scrapy.Request(absolute_url, callback=self.parse_job)
		
		pagination_link = response.css("nav.pagination a.Pagination-link")
		yield from response.follow_all(pagination_link, self.parse
		)
	
	def parse_job(self, response):
		title = response.css("div.h2::text").get()
		company = response.css("div.viewjob-labelWithIcon::text").get()
		application_link = response.url
		date = response.css("span.viewjob-age span::text").get()
		
		description_response = response.css("div.p *::text").getall()
		description = "".join(description_response)

		yield {
			"title": title,
			"company": company,
			"description": description,
			"application_link": application_link,
			"date": date
		}

	async def errback(self, failure):
		page = failure.request.meta["playwright_page"]
		await page.close()

