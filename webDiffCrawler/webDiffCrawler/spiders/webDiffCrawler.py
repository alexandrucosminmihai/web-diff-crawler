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

epsilon = 2

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
            # startRequests[-1].meta["id_crawlingrules"] = crawlingRule.id_crawlingrules
            # startRequests[-1].meta["address"] = crawlingRule.address
            # startRequests[-1].meta["selectionrule"] = crawlingRule.selectionrule
            # startRequests[-1].meta["content"] = crawlingRule.content
            startRequests[-1].meta["crawlingRuleEntry"] = crawlingRule

        # for currRequest in startRequests:
            # yield currRequest
        return startRequests

    def parse(self, response):
        global epsilon
        crawlingRule = response.meta["crawlingRuleEntry"]

        isFirstCrawl = True # Assume this is the first time we check this crawling rule
        lastCrawlTimestamp = 0

        currDateTime = datetime.datetime.now()

        if crawlingRule.lastcrawltime: # The rule was used before
            isFirstCrawl = False
            lastCrawlTimestamp = crawlingRule.lastcrawltime.timestamp()

        deltaTimestamp = currDateTime.timestamp() - lastCrawlTimestamp + epsilon
        self.log("currDateTime=" + str(currDateTime), logging.INFO)
        if isFirstCrawl:
            self.log("lastcrawltime=Never", logging.INFO)
        else:
            self.log("lastcrawltime=" + str(crawlingRule.lastcrawltime), logging.INFO)
        self.log("deltaTimestamp+epsilon=" + str(deltaTimestamp), logging.INFO)

        # Check whether the wait interval between two consecutive crawls has passed
        if (deltaTimestamp / 60) >= crawlingRule.crawlperiod:
            crawlingRule.lastcrawltime = currDateTime # A new crawl will begin

            currContent = response.css(crawlingRule.selectionrule).extract_first() # Extract the content using the rule
            currContent = html.escape(currContent)
            currContent = currContent.encode('unicode-escape').decode()
            self.log("currContent = " + currContent)
            oldContent = crawlingRule.content
            # oldContent = oldContent.encode('unicode-escape').decode()
            self.log("oldContent = " + oldContent)

            if not isFirstCrawl:
                # If there is some old content to compare the new content to
                self.sequenceMatcher.set_seqs(oldContent, currContent)
                operations = []
                if oldContent:
                    operations = self.sequenceMatcher.get_opcodes()

                if len(operations) == 1 and operations[0][0] == 'equal':
                    self.log("The content for id_crawlingrules=" + str(crawlingRule.id_crawlingrules)
                             + " hasn't changed so no new Notification was issued", logging.INFO)
                else:
                    self.log("The content for id_crawlingrules=" + str(crawlingRule.id_crawlingrules) +
                             " has changed => New notification issued", logging.INFO)

                    # Create a new notification and add it to the 'notifications' table
                    recipients = ["testUser"]
                    # id_notifications | address | matchingrule | id_matchingrule | modifytime | currcontent | oldcontent | changes | recipients | ackers
                    newNotification = mappedClasses.Notifications(address=crawlingRule.address,
                                                                  id_matchingrule=crawlingRule.id_crawlingrules,
                                                                  modifytime=crawlingRule.lastcrawltime,
                                                                  currcontent=currContent,
                                                                  oldcontent=oldContent,
                                                                  changes=json.dumps(operations), recipients=recipients, ackers=[])
                    self.session.add(newNotification)

                    crawlingRule.content = currContent
                    crawlingRule.lastmodifytime = datetime.datetime.now()
            else:
                # This is the first content we ever get for this rule
                self.log("This is the first crawl for id_crawlingrules=" + str(crawlingRule.id_crawlingrules)
                         + " so no new Notification was issued", logging.INFO)
                crawlingRule.content = currContent
                crawlingRule.lastmodifytime = datetime.datetime.now()

            self.session.add(crawlingRule)
            self.session.commit()
