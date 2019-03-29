import scrapy

import difflib
import logging
import datetime
import json
import html
import re
from w3lib.html import remove_tags, remove_tags_with_content, remove_comments
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import lxml

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

    # Crawler configurations
    DAILY_SCHEDULE_BEGIN = datetime.time(hour=0, minute=0)
    DAILY_SCHEDULE_END = datetime.time(hour=23, minute=59)
    TEXT_ONLY = True

    fileExtensions = ('.pdf', '.doc', '.docx', '.ppt', '.pps', '.txt', '.rar', '.zip', '.xls', '.7z', '.tar.gz')
    keptTags = ('ul', 'ol', 'li', 'a', 'p', 'br', 'code')

    # Convert relative URLs in anchor tags to absolute URLs
    @staticmethod
    def makeURLsAbsolute(baseURL, htmlContent):
        soup = BeautifulSoup(htmlContent, "lxml")
        for anchorTag in soup.find_all('a'):
            anchorTag['href'] = urljoin(baseURL, anchorTag['href'])

        return str(soup)

    @staticmethod
    def extractURLsToDocuments(htmlContent):
        documentsURLs = []
        soup = BeautifulSoup(htmlContent, "lxml")
        for anchorTag in soup.find_all('a'):
            if str(anchorTag['href']).endswith(webDiffCrawler.fileExtensions):
                documentsURLs.append(str(anchorTag))

        return documentsURLs

    # Remove any unnecessary whitespaces
    @staticmethod
    def cleanHtmlContent(dirtyHtml):
        cleanHtml = dirtyHtml
        cleanHtml = re.sub(r'\n+', r'\n', cleanHtml)  # Remove consecutive \n's
        cleanHtml = re.sub(r'\t+', r'\t', cleanHtml)  # Remove consecutive \t's
        cleanHtml = re.sub(r'(\n(\s)*\n)+', r'\n', cleanHtml)  # Replace consecutive \n's with whitespaces between them
        cleanHtml = re.sub(r'(\t(\s)*\t)+', r'\t', cleanHtml)  # Replace consecutive \t's with whitespaces between them
        cleanHtml = re.sub(r'(\n\t(\s)*)+', r'\n\t', cleanHtml)
        cleanHtml = re.sub(r'(\t\n(\s)*)+', r'\t\n', cleanHtml)
        cleanHtml = re.sub(r'>(\s)*<li', r'><li', cleanHtml)
        cleanHtml = re.sub(r'>(\s)*<ul', r'><ul', cleanHtml)
        cleanHtml = re.sub(r'>(\s)*<ol', r'><ol', cleanHtml)
        cleanHtml = re.sub(r'>(\s)*<p', r'><p', cleanHtml)
        cleanHtml = re.sub(r'>(\s)*</ul', r'></ul', cleanHtml)
        cleanHtml = re.sub(r'>(\s)*</ol', r'></ol', cleanHtml)
        cleanHtml = re.sub(r'>(\s)*</p', r'></p', cleanHtml)

        return cleanHtml

    def start_requests(self):
        startRequests = []
        currDateTime = datetime.datetime.now()

        # If the crawler is not meant to run at this time, don't do anything
        if not (webDiffCrawler.DAILY_SCHEDULE_BEGIN <= currDateTime.time() <= webDiffCrawler.DAILY_SCHEDULE_END):
            return startRequests

        self.sequenceMatcher = difflib.SequenceMatcher()
        self.session = webDiffCrawler.Session()

        for crawlingRule in self.session.query(mappedClasses.Crawlingrules).all():
            startRequests.append(scrapy.Request(url=crawlingRule.address, callback=self.parse))
            startRequests[-1].meta["crawlingRuleEntry"] = crawlingRule

        return startRequests

    def parse(self, response):
        global epsilon

        crawlingRule = response.meta["crawlingRuleEntry"]

        # Figure out if now is the time to crawl this rule and whether is the first crawl for the rule
        currDateTime = datetime.datetime.now()

        isFirstCrawl = True # Assume this is the first time we check this crawling rule
        isFirstCrawl = False # TODO
        lastCrawlTimestamp = 0

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
            selector = crawlingRule.selectionrule.replace('::text', '').strip()

            currContent = "".join(response.css(selector).extract())  # Extract all the content + tags using the selector

            if webDiffCrawler.TEXT_ONLY or '::text' in crawlingRule.selectionrule:
                # Ditch the script tags' content and then extract the text
                self.log("Extracting the text from the HTML...", logging.INFO)
                currContent = remove_tags(remove_tags_with_content(currContent, ('script', )),
                                          keep=webDiffCrawler.keptTags)
                currContent = remove_comments(currContent)
                currContent = webDiffCrawler.cleanHtmlContent(currContent)

            # Convert relative URLs to absolute URLs
            currContent = webDiffCrawler.makeURLsAbsolute(response.url, currContent)
            currContent = remove_tags(remove_tags_with_content(currContent, ('script',)),
                                      keep=webDiffCrawler.keptTags)
            # Extract URLs to downloadable documents
            currLinks = webDiffCrawler.extractURLsToDocuments(currContent)
            # currContent = html.escape(currContent)
            # currContent = currContent.replace("'", "\\'")
            # currContent = currContent.replace('"', '\\"')
            currContent = currContent.strip()
            # currContent = currContent.encode('unicode-escape').decode()  # Escape special chars like \n \t
            self.log("currContent = " + currContent)
            oldContent = crawlingRule.content
            oldLinks = crawlingRule.docslinks
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
                    recipients = ["all"]
                    # id_notifications | address | matchingrule | id_matchingrule | modifytime | currcontent | oldcontent | changes | recipients | ackers
                    newNotification = mappedClasses.Notifications(address=crawlingRule.address,
                                                                  id_matchingrule=crawlingRule.id_crawlingrules,
                                                                  modifytime=crawlingRule.lastcrawltime,
                                                                  currcontent=currContent,
                                                                  currdocslinks=json.dumps(currLinks),
                                                                  oldcontent=oldContent,
                                                                  olddocslinks=oldLinks,
                                                                  changes=json.dumps(operations),
                                                                  recipients=recipients,
                                                                  ackers=[])
                    self.session.add(newNotification)

                    crawlingRule.content = currContent
                    crawlingRule.docslinks = json.dumps(currLinks)
                    crawlingRule.lastmodifytime = datetime.datetime.now()
            else:
                # This is the first content we ever get for this rule
                self.log("This is the first crawl for id_crawlingrules=" + str(crawlingRule.id_crawlingrules)
                         + " so no new Notification was issued", logging.INFO)
                crawlingRule.content = currContent
                crawlingRule.docslinks = json.dumps(currLinks)
                crawlingRule.lastmodifytime = datetime.datetime.now()

            self.session.add(crawlingRule)
            self.session.commit()
