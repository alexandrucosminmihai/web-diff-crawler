import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Configure the secret key used for encryption
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Change me with something hard to guess'

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'postgresql://webdiffcrawler:clnr@localhost/webdiffcrawler'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'postgresql://webdiffcrawler:clnr@localhost/webdiffcrawler'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'postgresql://webdiffcrawler:clnr@localhost/webdiffcrawler'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}