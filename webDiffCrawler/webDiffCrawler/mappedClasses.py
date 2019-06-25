# Classes mapped by SQLAlchemy to database tables
from sqlalchemy import Column, Sequence, Integer, String, TIMESTAMP, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import JSONWebSignatureSerializer as Serializer
from flask import current_app

Base = declarative_base()


class Users(UserMixin, Base):
    __tablename__ = 'users'
    id_users = Column(Integer, Sequence('users_id_users_seq'), primary_key=True)
    email = Column(String(64), unique=True) # nullable and unique is ok in postgres
    username = Column(String(64), unique=True)
    password_hash = Column(String(128))
    secrettoken = Column(String(128))
    id_roles = Column(Integer)

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def get_id(self):
        return str(self.id_users)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generateToken(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'confirm': self.id_users}).decode('utf-8')

    def confirmToken(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False

        if data.get('confirm') != self.id_users:
            return False

        return True


class Crawlingrules(Base):
    __tablename__ = 'crawlingrules'
    id_crawlingrules = Column(Integer, Sequence('crawlingrules_id_crawlingrules_seq'), primary_key=True)
    address = Column(String)
    selectionrule = Column(String)
    lastmodifytime = Column(TIMESTAMP(True))
    lastcrawltime = Column(TIMESTAMP(True))
    crawlperiod = Column(Integer, nullable=False)
    contributor = Column(String)
    description = Column(String)
    content = Column(String)
    docslinks = Column(String)

    def __repr__(self):
        return "<Crawlingrule(id_crawlingrules='%s', address='%s', selectionrule='%s', lastmodifytime='%s', " \
               "contributor='%s', content='%s')>" % (self.id_crawlingrules, self.address, self.selectionrule,
                                                     self.lastmodifytime, self.contributor, self.content)

# id_notifications | address | id_matchingrule | modifytime | oldcontent | changes | recipients | ackers
class Notifications(Base):
    __tablename__ = 'notifications'
    id_notifications = Column(Integer, Sequence('notifications_id_notifications_seq'), primary_key=True)
    address = Column(String, nullable=False)
    # matchingrule = Column(String, nullable=False)
    id_matchingrule = Column(Integer)
    modifytime = Column(TIMESTAMP(True))
    currcontent = Column(String)
    coloredcurrcontent = Column(String)
    currdocslinks = Column(String)
    detectedreplacedorinserted = Column(String)
    oldcontenttime = Column(TIMESTAMP(True))
    oldcontent = Column(String)
    coloredoldcontent = Column(String)
    olddocslinks = Column(String)
    detecteddeleted = Column(String)
    changes = Column(String, nullable=False)
    recipients = Column(ARRAY(String))
    ackers = Column(ARRAY(String)) # It's an array in case of future use. Normally should have maximum 1 element

    def __repr__(self):
        return "<Notification(id_notifications='%s', address='%s', matchingrule='%s', id_matchingrule='%s'," \
               " modifytime='%s', oldcontent='%s', changes='%s' recipients='%s', ackers='%s')>" % \
               (self.id_notifications, self.address, self.matchingrule, self.id_matchingrule, self.modifytime,
                self.oldcontent, self.changes, self.recipients, self.ackers)


class Configurations(Base):
    __tablename__ = 'configurations'
    id_configurations = Column(Integer, Sequence('configurations_id_configurations_seq'), primary_key=True)
    runmode = Column(Integer)
    dailyschedulebegin = Column(TIMESTAMP(True))
    dailyscheduleend = Column(TIMESTAMP(True))

    def __repr__(self):
        return "<Configuration(id_configurations='%s', runmode='%s', dailyschedulebegin='%s', dailyscheduleend='%s'" % \
               (self.id_configurations, self.runmode, self.dailyschedulebegin, self.dailyscheduleend)

