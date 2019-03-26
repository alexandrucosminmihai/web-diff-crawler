# Classes mapped by SQLAlchemy to database tables
from sqlalchemy import Column, Sequence, Integer, String, TIMESTAMP, ARRAY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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
    oldcontent = Column(String)
    changes = Column(String, nullable=False)
    recipients = Column(ARRAY(String))
    ackers = Column(ARRAY(String)) # It's an array in case of future use. Normally should have maximum 1 element

    def __repr__(self):
        return "<Notification(id_notifications='%s', address='%s', matchingrule='%s', id_matchingrule='%s'," \
               " modifytime='%s', oldcontent='%s', changes='%s' recipients='%s', ackers='%s')>" % \
               (self.id_notifications, self.address, self.matchingrule, self.id_matchingrule, self.modifytime,
                self.oldcontent, self.changes, self.recipients, self.ackers)
