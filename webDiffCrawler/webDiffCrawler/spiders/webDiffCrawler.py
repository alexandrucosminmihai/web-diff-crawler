import scrapy

import difflib
import logging
import datetime

# SQLAclhemy related imports
from .. import mappedClasses
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class webDiffCrawler(scrapy.Spider):
    name = "webDiffCrawler"

    # SQLAlchemy attributes
    engine = create_engine('postgresql://webdiffcrawler:clnr@localhost/webdiffcrawler', echo=True)
    Session = sessionmaker(bind=engine)

    def start_requests(self):
        self.sequenceMatcher = difflib.SequenceMatcher()
        self.session = webDiffCrawler.Session()
        startRequests = []

        for crawlingRule in self.session.query(mappedClasses.Crawlingrules).all():
            startRequests.append(scrapy.Request(url=crawlingRule.address, callback=self.parse))
            startRequests[-1].meta["id_crawlingrules"] = crawlingRule.id_crawlingrules
            startRequests[-1].meta["address"] = crawlingRule.address
            startRequests[-1].meta["selectionrule"] = crawlingRule.selectionrule
            startRequests[-1].meta["content"] = crawlingRule.content

        # for currRequest in startRequests:
            # yield currRequest
        return startRequests

    def parse(self, response):
        currContent = response.css(response.meta["selectionrule"]).extract_first()
        oldContent = response.meta["content"]

        self.sequenceMatcher.set_seqs(currContent, oldContent)
        operations = self.sequenceMatcher.get_opcodes()

        if len(operations) == 1 and operations[0][0] == 'equal':
            self.log("The content for id_crawlingrules=" + str(response.meta["id_crawlingrules"]) + " hasn't changed",
                     logging.INFO)
        else:
            self.log("The content for id_crawlingrules=" + str(response.meta["id_crawlingrules"]) +
                     " has changed => New notification issued", logging.INFO)

            # Create a new notification and add it to the 'notifications' table
            recipients = ["testUser"] # TODO: get all the users from a possibly already existing users database
            newNotification = mappedClasses.Notifications(address=response.meta["address"],
                                                          matchingrule=response.meta["selectionrule"],
                                                          modifytime=datetime.datetime.now(),
                                                          content=str(operations), recipients=recipients, ackers=[])
            self.session.add(newNotification)

            crawlingRule = self.session.query(mappedClasses.Crawlingrules).\
                filter_by(id_crawlingrules=response.meta["id_crawlingrules"]).first()
            crawlingRule.content = currContent
            crawlingRule.lastmodifytime = datetime.datetime.now()
            self.session.add(crawlingRule)

            self.session.commit()
