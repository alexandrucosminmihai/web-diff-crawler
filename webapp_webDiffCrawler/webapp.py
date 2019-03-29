import os
from webapp_webDiffCrawler.app import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# import webDiffCrawler.webDiffCrawler.mappedClasses as mappedClasses
