from flask import Flask, render_template, url_for, redirect, flash, request

# Flask extensions imports
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import webapp.forms
import datetime
import sys

import webDiffCrawler.webDiffCrawler.mappedClasses as mappedClasses

app = Flask(__name__)  # Create the Flask app instance that will handle the requests
app.config['SECRET_KEY'] = 'Change me with something hard to guess' # Configure the secret key used for encryption
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://webdiffcrawler:clnr@localhost/webdiffcrawler'

bootstrap = Bootstrap(app)  # Bootstrap extension initialization
moment = Moment(app)  # Extension that uses the Moment.js library to convert UTC time to client time

# SQLAlchemy attributes
engine = create_engine('postgresql://webdiffcrawler:clnr@localhost/webdiffcrawler', echo=True)
DBSession = sessionmaker(bind=engine)
dbSession = DBSession()


@app.route('/')  # Add a route that maps the '/' URL to the 'index' view (handling) function
def index():
    # return '<h1>Hello, world!</h1>'
    # return render_template('index.html') # Render the given template using Jinja2 and return the resulting html
    return redirect(url_for('notifications'))


@app.route('/ackanotification', methods=['POST'])
def ackANotification():
    currentUser = "testUser"
    notifId = request.form['ackNotificationId']
    notifToAck = dbSession.query(mappedClasses.Notifications).filter_by(id_notifications=notifId).first()
    notifToAck.ackers = list(notifToAck.ackers)
    notifToAck.ackers.append(currentUser)
    dbSession.commit()
    return redirect(url_for('notifications'))


@app.route('/acknotifications', methods=['POST'])
def ackNotifications():
    currentUser = "testUser"
    idsToAck = request.form.getlist('ack_checkbox')
    if idsToAck:
        for notfId in idsToAck:
            notifToAck = dbSession.query(mappedClasses.Notifications).filter_by(id_notifications=notfId).first()
            notifToAck.ackers = list(notifToAck.ackers)
            notifToAck.ackers.append(currentUser)

        dbSession.commit()

    return redirect(url_for('notifications'))


@app.route('/notifications')
def notifications():
    notifications = []
    for notif in \
            dbSession.query(mappedClasses.Notifications).filter(mappedClasses.Notifications.ackers==[]).\
                    order_by(mappedClasses.Notifications.id_notifications.desc()):
        currNotif = dict()
        currNotif['id_notifications'] = notif.id_notifications
        currNotif['address'] = notif.address
        currNotif['matchingrule'] = notif.matchingrule
        currNotif['modifytime'] = notif.modifytime
        notifications.append(currNotif)

    return render_template('notifications.html', notifications=notifications)


@app.route('/deletearule', methods=['POST'])
def deleteACrawlingRule():
    ruleId = request.form['deleteCrawlingRuleId']
    ruleToDelete = dbSession.query(mappedClasses.Crawlingrules).filter_by(id_crawlingrules=ruleId).first()
    dbSession.delete(ruleToDelete)
    dbSession.commit()
    return redirect(url_for('crawlingRules'))


@app.route('/deleterules', methods=['POST'])
def deleteCrawlingRules():
    idsToDelete = request.form.getlist('delete_checkbox')
    if idsToDelete:
        for ruleId in idsToDelete:
            ruleToDelete = dbSession.query(mappedClasses.Crawlingrules).filter_by(id_crawlingrules=ruleId).first()
            dbSession.delete(ruleToDelete)

        dbSession.commit()

    return redirect(url_for('crawlingRules'))


@app.route('/crawlingrules', methods=['GET', 'POST'])
def crawlingRules():
    # Create the form to be rendered
    crawlingRuleForm = webapp.forms.CrawlingRuleForm(address="https://en.wikipedia.org/wiki/Internet")

    address = None
    selector = None

    print('DEBUG: crawlingRules()', file=sys.stdout)

    if crawlingRuleForm.submit.data:
        if crawlingRuleForm.validate_on_submit():
            address = request.form['address']
            selector = request.form['selector']

            newCrawlingRule = mappedClasses.Crawlingrules(address=address, selectionrule=selector,
                                                          lastmodifytime=datetime.datetime.now(),
                                                          contributor='testUser',
                                                          content='<~Empty~>')
            dbSession.add(newCrawlingRule)
            dbSession.commit()

            displayAddress = address
            if len(displayAddress) > 45:
                displayAddress = displayAddress[:44] + '[...]'
            flash('Crawling rule: address="' + displayAddress + '" with selector="' + selector + '" has been added.')
        else:
            flash('No rule has been added.')

        return redirect(url_for('crawlingRules'))

    rules = []
    for crawlingRule in dbSession.query(mappedClasses.Crawlingrules).all():
        currRule = dict()
        currRule['id_crawlingrules'] = crawlingRule.id_crawlingrules
        currRule['address'] = crawlingRule.address
        currRule['selectionrule'] = crawlingRule.selectionrule
        rules.append(currRule)

    return render_template('crawlingrules.html', crawlingRuleForm=crawlingRuleForm, crawlingRules=rules)


@app.route('/christmas/<username>') # Dynamic route
def christmas(username):
    # return '<h1>Merry Christmas, %s!'%username.upper()
    return render_template('user.html', name=username)


@app.errorhandler(404)
def error404(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def error500(e):
    return render_template('500.html'), 500
