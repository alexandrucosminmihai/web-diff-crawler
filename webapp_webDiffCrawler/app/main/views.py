import datetime
import sys
from . import main
from .. import dbSession
from flask import Flask, render_template, url_for, redirect, flash, request, abort
from webDiffCrawler.webDiffCrawler.mappedClasses import Notifications, Crawlingrules
from .forms import CrawlingRuleForm

@main.route('/')  # Add a route that maps the '/' URL to the 'index' view (handling) function
def index():
    # return '<h1>Hello, world!</h1>'
    # return render_template('index.html') # Render the given template using Jinja2 and return the resulting html
    return redirect(url_for('main.notifications'))

@main.route('/ackanotification', methods=['POST'])
def ackANotification():
    currentUser = "testUser"
    notifId = request.form['ackNotificationId']
    notifToAck = dbSession.query(Notifications).filter_by(id_notifications=notifId).first()
    notifToAck.ackers = list(notifToAck.ackers)
    notifToAck.ackers.append(currentUser)
    dbSession.commit()
    return redirect(url_for('main.notifications'))


@main.route('/acknotifications', methods=['POST'])
def ackNotifications():
    currentUser = "testUser"
    idsToAck = request.form.getlist('ack_checkbox')
    if idsToAck:
        for notfId in idsToAck:
            notifToAck = dbSession.query(Notifications).filter_by(id_notifications=notfId).first()
            notifToAck.ackers = list(notifToAck.ackers)
            notifToAck.ackers.append(currentUser)

        dbSession.commit()

    return redirect(url_for('main.notifications'))


@main.route('/notifications')
def notifications():
    notifications = []
    matchingRule = None
    for notif in \
            dbSession.query(Notifications).filter(Notifications.ackers==[]).\
                    order_by(Notifications.id_notifications.desc()):
        matchingRule = dbSession.query(Crawlingrules).\
            filter_by(id_crawlingrules=notif.id_matchingrule).first()
        currNotif = dict()
        currNotif['id_notifications'] = notif.id_notifications
        currNotif['address'] = notif.address
        currNotif['modifytime'] = notif.modifytime
        currNotif['modifytimestr'] = notif.modifytime.strftime("%a, %d-%m-%Y, %H:%M")
        if matchingRule:
            currNotif['matchingrule'] = matchingRule.selectionrule
            currNotif['ruleDescription'] = matchingRule.description
        else:
            currNotif['matchingrule'] = "Not available"
            currNotif['ruleDescription'] = "Not available"
        notifications.append(currNotif)

    return render_template('notifications.html', notifications=notifications)

@main.route('/notifications/<id_notifications>')
def reviewNotification(id_notifications):
    notificationRow = dbSession.query(Notifications).\
        filter(Notifications.id_notifications==id_notifications).first()
    matchingRule = dbSession.query(Crawlingrules).\
        filter_by(id_crawlingrules=notificationRow.id_matchingrule).first()

    if notificationRow is None:
        abort(404)

    currNotif = dict()
    currNotif['id_notifications'] = notificationRow.id_notifications
    currNotif['address'] = notificationRow.address
    if matchingRule:
        currNotif['matchingrule'] = matchingRule.selectionrule
    else:
        currNotif['matchingrule'] = "Not available"
    currNotif['modifytime'] = notificationRow.modifytime
    currNotif['modifytimestr'] = notificationRow.modifytime.strftime("%A, %d-%m-%Y, %H:%M")
    currNotif['currcontent'] = notificationRow.currcontent
    currNotif['oldcontent'] = notificationRow.oldcontent
    currNotif['changes'] = notificationRow.changes # Keep the changes in the json format, as given by the database
    # currNotif['changes'] = json.loads(notificationRow.changes)

    return render_template('review_notification.html', notification=currNotif)


@main.route('/deletearule', methods=['POST'])
def deleteACrawlingRule():
    ruleId = request.form['deleteCrawlingRuleId']
    ruleToDelete = dbSession.query(Crawlingrules).filter_by(id_crawlingrules=ruleId).first()
    dbSession.delete(ruleToDelete)
    dbSession.commit()
    return redirect(url_for('main.crawlingRules'))


@main.route('/deleterules', methods=['POST'])
def deleteCrawlingRules():
    idsToDelete = request.form.getlist('delete_checkbox')
    if idsToDelete:
        for ruleId in idsToDelete:
            ruleToDelete = dbSession.query(Crawlingrules).filter_by(id_crawlingrules=ruleId).first()
            dbSession.delete(ruleToDelete)

        dbSession.commit()

    return redirect(url_for('main.crawlingRules'))


@main.route('/crawlingrules', methods=['GET', 'POST'])
def crawlingRules():
    # Create the form to be rendered
    # crawlingRuleForm = webapp.forms.CrawlingRuleForm(address="https://en.wikipedia.org/wiki/Internet")
    crawlingRuleForm = \
        CrawlingRuleForm(address="https://www.cjmaramures.ro/activitate/comunicare/comunicate-de-presa")

    address = None
    selector = None

    print('DEBUG: crawlingRules()', file=sys.stdout)

    if crawlingRuleForm.submit.data:
        if crawlingRuleForm.validate_on_submit():
            address = request.form['address']
            selector = request.form['selector']
            description = request.form['description']
            crawlPeriodUnit = request.form['crawlPeriodUnitType']
            crawlPeriod = request.form['crawlPeriod']

            # The crawlPeriod is stored as number of minutes in the database
            if crawlPeriodUnit == 'hours':
                crawlPeriod *= 60

            newCrawlingRule = Crawlingrules(address=address, selectionrule=selector,
                                                          lastmodifytime=datetime.datetime.now(),
                                                          contributor='testUser',
                                                          content='<~Empty~>',
                                                          crawlperiod=crawlPeriod,
                                                          description=description)
            dbSession.add(newCrawlingRule)
            dbSession.commit()

            displayAddress = address
            if len(displayAddress) > 45:
                displayAddress = displayAddress[:44] + '[...]'
            flash('Crawling rule: address="' + displayAddress + '" with selector="' + selector + '" has been added.')
        else:
            flash('No rule has been added.')

        return redirect(url_for('main.crawlingRules'))

    rules = []
    for crawlingRule in dbSession.query(Crawlingrules)\
            .order_by(Crawlingrules.id_crawlingrules.desc()):
        currRule = dict()
        currRule['id_crawlingrules'] = crawlingRule.id_crawlingrules
        currRule['address'] = crawlingRule.address
        currRule['selectionrule'] = crawlingRule.selectionrule
        currRule['description'] = crawlingRule.description
        currRule['lastymodifytime'] = crawlingRule.lastmodifytime
        currRule['lastmodifytimestr'] = crawlingRule.lastmodifytime.strftime("%A, %d-%m-%Y, %H:%M")
        rules.append(currRule)

    return render_template('crawlingrules.html', crawlingRuleForm=crawlingRuleForm, crawlingRules=rules)
