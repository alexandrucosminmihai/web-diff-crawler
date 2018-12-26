from flask import Flask, render_template, url_for, redirect, flash

# Flask extensions imports
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import webapp.forms
import datetime

import webDiffCrawler.webDiffCrawler.mappedClasses as mappedClasses

app = Flask(__name__) # Create the Flask app instance that will handle the requests
app.config['SECRET_KEY'] = 'Change me with something hard to guess' # Configure the secret key used for encryption
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://webdiffcrawler:clnr@localhost/webdiffcrawler'

bootstrap = Bootstrap(app) # Bootstrap extension initialization
moment = Moment(app) # Extension that uses the Moment.js library to convert UTC time to client time

# SQLAlchemy attributes
engine = create_engine('postgresql://webdiffcrawler:clnr@localhost/webdiffcrawler', echo=True)
Session = sessionmaker(bind=engine)
session = Session()


@app.route('/') # Add a route that maps the '/' URL to the 'index' view (handling) function
def index():
    # return '<h1>Hello, world!</h1>'
    # return render_template('index.html') # Render the given template using Jinja2 and return the resulting html
    return redirect(url_for('notifications'))


@app.route('/notifications')
def notifications():
    print()


@app.route('/crawlingrules', methods=['GET', 'POST'])
def crawlingrules():
    crawlingRuleForm = webapp.forms.CrawlingRuleForm() # Create the form to be rendered

    # Fields to store the data from the forms
    address = None
    selector = None

    if crawlingRuleForm.validate_on_submit():
        address = crawlingRuleForm.address.data
        selector = crawlingRuleForm.selector.data

        newCrawlingRule = mappedClasses.Crawlingrules(address=address, selectionrule=selector,
                                                      lastmodifytime=datetime.datetime.now(), contributor='testUser',
                                                      content='<~Empty~>')
        session.add(newCrawlingRule)
        session.commit()

        displayAddress = address
        if len(displayAddress) > 45:
            displayAddress = displayAddress[:44] + '[...]'
        flash('Crawling rule: address="' + displayAddress + '" with selector="' + selector + '" has been added.')
        return redirect(url_for('crawlingrules')) # Post-Redirect-Get

    rules = []
    for crawlingRule in session.query(mappedClasses.Crawlingrules).all():
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
