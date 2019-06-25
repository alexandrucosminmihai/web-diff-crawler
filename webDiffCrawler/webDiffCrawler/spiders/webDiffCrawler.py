"""
Versiune 1:
Retin o lista cu pozitiile tag-urilor : index < si index >
Parcurg toate elementele de diff si elimin bucatiile din diferente care se afla in interiorul tag-urilor
    Versiune 1.1 O(N * M) 2 for-uri imbricate
    Versiune 1.2 O(N log M) sau O(M log N) cautare binara
"""

import scrapy

import difflib
import logging
import datetime
import copy
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


def extractTagsIntervals(content):
    sol = [] # An array of tag intervals (represented as arrays of dim 2)
    for i in range(len(content)):
        if content[i] == '<':
            sol.append([i])
        elif content[i] == '>':
            if len(sol) == 0:
                continue
            if len(sol[-1]) >= 2:
                continue

            sol[-1].append(i)

    return sol


# Some operations might be removed, some new operations might be created by splitting existing operations
def removeTagsFromOperations(operations, opStart, opEnd, tagsIntervals):
    finalOperations = []
    currOperations = copy.deepcopy(operations)

    globalFoundTag = True

    # Remove parts of operations that regard HTML tags
    # O(N * M) todo: improve. at least binary search
    while globalFoundTag:
        globalFoundTag = False
        finalOperations = []
        for operation in currOperations:
            foundTag = False  # Found intersecting tag for this operation
            for tag in tagsIntervals:
                if tag[0] <= operation[opStart] and operation[opEnd] <= tag[1]:  # The whole operation is inside the tag
                    foundTag = True
                    globalFoundTag = True
                    break
                elif tag[0] >= operation[opStart] and tag[1] <= operation[opEnd]:  # The whole tag is inside the operation
                    leftOperation = [operation[0], -1, -1, -1, -1]
                    leftOperation[opStart] = operation[opStart]
                    leftOperation[opEnd] = tag[0] - 1
                    #leftOperation = [operation[0], -1, -1, operation[opStart], tag[0] - 1]
                    rightOperation = [operation[0], -1, -1, -1, -1]
                    rightOperation[opStart] = tag[1] + 1
                    rightOperation[opEnd] = operation[opEnd]
                    #rightOperation = [operation[0], -1, -1, tag[1] + 1, operation[opEnd]]
                    if leftOperation[opStart] <= leftOperation[opEnd]:
                        finalOperations.append(leftOperation)
                    if rightOperation[opStart] <= rightOperation[opEnd]:
                        finalOperations.append(rightOperation)
                    foundTag = True
                    globalFoundTag = True
                    break
                elif tag[0] < operation[opStart] and tag[1] >= operation[opStart] and tag[1] <= operation[opEnd]:
                    newOperation = [operation[0], -1, -1, -1, -1]
                    newOperation[opStart] = tag[1] + 1
                    newOperation[opEnd] = operation[opEnd]
                    #newOperation = [operation[0], -1, -1, tag[1] + 1, operation[opEnd]]
                    if newOperation[opStart] <= newOperation[opEnd]:
                        finalOperations.append(newOperation)
                    foundTag = True
                    globalFoundTag = True
                    break
                elif tag[0] > operation[opStart] and tag[0] <= operation[opEnd]:
                    #newOperation = [operation[0], -1, -1, operation[opStart], tag[0] - 1]
                    newOperation = [operation[0], -1, -1, -1, -1]
                    newOperation[opStart] = operation[opStart]
                    newOperation[opEnd] = tag[0] - 1
                    if newOperation[opStart] <= newOperation[opEnd]:
                        finalOperations.append(newOperation)
                    foundTag = True
                    globalFoundTag = True
                    break

            if not foundTag:
                finalOperations.append(operation)

        currOperations = finalOperations

    return finalOperations


# Add HTML tags for colors inside content, without affecting the differences in HTML tags
def colorDifferences(newContent, oldContent, operations, newTagsIntervals, oldTagsIntervals):
    detectedReplacedOrInserted = ""
    detectedDeleted = ""
    coloredNewContent = newContent
    coloredOldContent = oldContent
    newContentAddedCharsNum = 0
    oldContentAddedCharsNum = 0

    colors = {}
    colors["insert"] = {}
    colors["insert"]["before"] = '<span style="background-color: yellow">' # Maybe use a different color
    colors["insert"]["after"] = '</span>'
    colors["insert"]["beforelen"] = len(colors["insert"]["before"])
    colors["insert"]["afterlen"] = len(colors["insert"]["after"])

    # colors["red"] = {}
    # colors["red"]["before"] = '<span style="background-color: red">'
    # colors["red"]["after"] = '</span>'
    colors["replace"] = {}
    colors["replace"]["before"] = '<span style="background-color: yellow">'
    colors["replace"]["after"] = '</span>'
    colors["replace"]["beforelen"] = len(colors["replace"]["before"])
    colors["replace"]["afterlen"] = len(colors["replace"]["after"])

    colors["delete"] = {}
    colors["delete"]["before"] = '<span style="background-color: red">'
    colors["delete"]["after"] = '</span>'
    colors["delete"]["beforelen"] = len(colors["delete"]["before"])
    colors["delete"]["afterlen"] = len(colors["delete"]["after"])

    # Create the colored newContent and extract newly added text
    finalOperationsNewContent = removeTagsFromOperations(operations, 3, 4, newTagsIntervals)

    for operation in finalOperationsNewContent:
        start = operation[3] + newContentAddedCharsNum
        end = operation[4] + newContentAddedCharsNum
        leftText = coloredNewContent[:start]
        targetText = coloredNewContent[start:end + 1]
        rightText = coloredNewContent[end + 1:]
        if operation[0] in ["insert", "replace"]:
            coloredNewContent = leftText + colors[operation[0]]["before"] + targetText + colors[operation[0]]["after"] + rightText
            newContentAddedCharsNum += colors[operation[0]]["beforelen"] + colors[operation[0]]["afterlen"]
            detectedReplacedOrInserted += targetText
        # else don't do anything

    # Create the colored oldContent and extract deleted old text
    finalOperationsOldContent = removeTagsFromOperations(operations, 1, 2, oldTagsIntervals)

    for operation in finalOperationsOldContent:
        start = operation[1] + oldContentAddedCharsNum
        end = operation[2] + oldContentAddedCharsNum
        leftText = coloredOldContent[:start]
        targetText = coloredOldContent[start:end + 1]
        rightText = coloredOldContent[end + 1:]
        if operation[0] in ["delete"]:
            coloredOldContent = leftText + colors[operation[0]]["before"] + targetText + colors[operation[0]]["after"] + rightText
            oldContentAddedCharsNum += colors[operation[0]]["beforelen"] + colors[operation[0]]["afterlen"]
            detectedDeleted += targetText
        # else don't do anything

    return coloredNewContent, detectedReplacedOrInserted, coloredOldContent, detectedDeleted


class webDiffCrawler(scrapy.Spider):
    name = "webDiffCrawler"

    # SQLAlchemy attributes
    engine = create_engine('postgresql://webdiffcrawler:clnr@localhost/webdiffcrawler', echo=True)
    Session = sessionmaker(bind=engine)

    # Crawler configurations
    # DAILY_SCHEDULE_BEGIN = datetime.time(hour=0, minute=0)
    # DAILY_SCHEDULE_END = datetime.time(hour=23, minute=59)
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
        self.sequenceMatcher = difflib.SequenceMatcher()
        self.session = webDiffCrawler.Session()
        self.configuration = self.session.query(mappedClasses.Configurations).first()

        dailyScheduleBegin = self.configuration.dailyschedulebegin
        dailyScheduleEnd = self.configuration.dailyscheduleend

        self.shouldRun = True

        # If the crawler is deactivated
        if self.configuration.runmode == 0:
            self.shouldRun = False
            self.log("The crawler shouldn't run because runmode=" + str(self.configuration.runmode), logging.INFO)
            return startRequests

        # If the crawler is not meant to run at this time, don't do anything
        timeBegin = datetime.time(hour=dailyScheduleBegin.hour, minute=dailyScheduleBegin.minute)
        timeMidnight = datetime.time(hour=0, minute=0)
        timeEnd = datetime.time(hour=dailyScheduleEnd.hour, minute=dailyScheduleEnd.minute)
        timeCurr = currDateTime.time()

        if timeBegin <= timeEnd: # If the interval does not include midnight (00:00)
            if not (timeBegin <= timeCurr <= timeEnd):
                self.shouldRun = False
        else: # If midnight is in the interval, check whether now is in [begin, midnight] or (midnight, end]
            if not ((timeBegin <= timeCurr <= timeMidnight) or (timeMidnight <= timeCurr <= timeEnd)):
                self.shouldRun = False

        if not self.shouldRun:
            self.log("The crawler shouldn't run because it's out of schedule", logging.INFO)
            return startRequests

        for crawlingRule in self.session.query(mappedClasses.Crawlingrules).all():
            startRequests.append(scrapy.Request(url=crawlingRule.address, callback=self.parse))
            startRequests[-1].meta["crawlingRuleEntry"] = crawlingRule

        return startRequests

    def parse(self, response):
        global epsilon

        shouldCrawlRule = True

        crawlingRule = response.meta["crawlingRuleEntry"]

        # Figure out if now is the time to crawl this rule and whether is the first crawl for the rule
        currDateTime = datetime.datetime.now()

        isFirstCrawl = True # Assume this is the first time we check this crawling rule
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
        if (deltaTimestamp / 60) < crawlingRule.crawlperiod:
            shouldCrawlRule = False
            return

        if shouldCrawlRule:
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
                newContentTagsIntervals = extractTagsIntervals(currContent)
                oldContentTagsIntervals = extractTagsIntervals(oldContent)

                if oldContent:
                    operations = self.sequenceMatcher.get_opcodes()

                if len(operations) == 1 and operations[0][0] == 'equal':
                    self.log("The content for id_crawlingrules=" + str(crawlingRule.id_crawlingrules)
                             + " hasn't changed so no new Notification was issued", logging.INFO)
                else:
                    self.log("The content for id_crawlingrules=" + str(crawlingRule.id_crawlingrules) +
                             " has changed => New notification issued", logging.INFO)

                    # Update the operations interval indices in order for all the intervals to be closed
                    for operation in operations:
                        operation = list(operation)
                        self.log("Initial Operation: " + str(operation), logging.DEBUG)
                        operation[2] -= 1
                        if operation[2] < operation[1]:
                            operation[2] = operation[1]

                        operation[4] -= 1
                        if operation[4] < operation[3]:
                            operation[4] = operation[3]

                        self.log("Final Operation: " + str(operation), logging.DEBUG)

                    # Generate colored HTML code
                    #coloredCurrContent, detecte = colorDifferences(currContent, operations, tagsIntervals)
                    coloredCurrContent, detectedReplacedOrInserted, coloredOldContent, detectedDeleted = colorDifferences(currContent, oldContent, operations, newContentTagsIntervals, oldContentTagsIntervals)

                    # Create a new notification and add it to the 'notifications' table
                    recipients = ["all"]
                    newNotification = mappedClasses.Notifications(address=crawlingRule.address,
                                                                  id_matchingrule=crawlingRule.id_crawlingrules,
                                                                  modifytime=crawlingRule.lastcrawltime,
                                                                  currcontent=currContent,
                                                                  coloredcurrcontent=coloredCurrContent,
                                                                  currdocslinks=json.dumps(currLinks),
                                                                  detectedreplacedorinserted=detectedReplacedOrInserted,
                                                                  oldcontenttime=crawlingRule.lastmodifytime,
                                                                  oldcontent=oldContent,
                                                                  coloredoldcontent=coloredOldContent,
                                                                  detecteddeleted=detectedDeleted,
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
