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
    contributor = Column(String)
    content = Column(String)

    def __repr__(self):
        return "<Crawlingrule(id_crawlingrules='%s', address='%s', selectionrule='%s', lastmodifytime='%s', " \
               "contributor='%s', content='%s')>" % (self.id_crawlingrules, self.address, self.selectionrule,
                                                     self.lastmodifytime, self.contributor, self.content)

# id_notifications | address | matchingrule | modifytime | content | recipients | ackers
class Notifications(Base):
    __tablename__ = 'notifications'
    id_notifications = Column(Integer, Sequence('notifications_id_notifications_seq'), primary_key=True)
    address = Column(String)
    matchingrule = Column(String)
    modifytime = Column(TIMESTAMP(True))
    content = Column(String)
    recipients = Column(ARRAY(String))
    ackers = Column(ARRAY(String)) # It's an array in case of future use. Normally should have maximum 1 element

    def __repr__(self):
        return "<Notification(id_notifications='%s', address='%s', matchingrule='%s', modifytime='%s', " \
               "content='%s', recipients='%s', ackers='%s')>" % (self.id_notifications, self.address,
                                                                 self.matchingrule, self.modifytime, self.content,
                                                                 self.recipients, self.ackers)
