import scrapy

# SQLAclhemy related imports
from .. import mappedClasses
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class webDiffCrawler(scrapy.Spider):
    name = "webDiffCrawler"

    # SQLAlchemy attributes
    engine = create_engine('postgresql://webdiffcrawler:clnr@localhost/webdiffcrawler', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    def start_requests(self):
        startRequests = []

        for crawlingRule in webDiffCrawler.session.query(mappedClasses.Crawlingrules).all():
            startRequests.append(scrapy.Request(url=crawlingRule.address, callback=self.parse))
            startRequests[-1].meta["selectionrule"] = crawlingRule.selectionrule
            startRequests[-1].meta["id_selectionrules"] = crawlingRule.id_crawlingrules
            startRequests[-1].meta["content"] = crawlingRule.content

        for currRequest in startRequests:
            yield currRequest

    def parse(self, response):
        print("I made the request for the rule: " + str(response.meta["id_selectionrules"]))
