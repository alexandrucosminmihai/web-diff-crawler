import scrapy

import difflib
import logging
import datetime
import json
import html

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
        currContent = response.css(response.meta["selectionrule"]).extract_first() # Extract the content using the rule
        currContent = html.escape(currContent)
        currContent = currContent.encode('unicode-escape').decode()
        self.log("currContent = " + currContent)
        oldContent = response.meta["content"]
        # oldContent = oldContent.encode('unicode-escape').decode()
        self.log("oldContent = " + oldContent)

        self.sequenceMatcher.set_seqs(oldContent, currContent)
        operations = []
        if oldContent:
            operations = self.sequenceMatcher.get_opcodes()

        if len(operations) == 1 and operations[0][0] == 'equal':
            self.log("The content for id_crawlingrules=" + str(response.meta["id_crawlingrules"]) + " hasn't changed",
                     logging.INFO)
        else:
            self.log("The content for id_crawlingrules=" + str(response.meta["id_crawlingrules"]) +
                     " has changed => New notification issued", logging.INFO)

            # Create a new notification and add it to the 'notifications' table
            recipients = ["testUser"]
            # id_notifications | address | matchingrule | id_matchingrule | modifytime | currcontent | oldcontent | changes | recipients | ackers
            newNotification = mappedClasses.Notifications(address=response.meta["address"],
                                                          id_matchingrule=response.meta["id_crawlingrules"],
                                                          modifytime=datetime.datetime.now(),
                                                          currcontent=currContent,
                                                          oldcontent=oldContent,
                                                          changes=json.dumps(operations), recipients=recipients, ackers=[])
            self.session.add(newNotification)

            crawlingRule = self.session.query(mappedClasses.Crawlingrules).\
                filter_by(id_crawlingrules=response.meta["id_crawlingrules"]).first()
            crawlingRule.content = currContent
            crawlingRule.lastmodifytime = datetime.datetime.now()
            self.session.add(crawlingRule)

            self.session.commit()
