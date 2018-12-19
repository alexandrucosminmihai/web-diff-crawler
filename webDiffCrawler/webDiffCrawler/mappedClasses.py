# Classes mapped by SQLAlchemy to database tables
from sqlalchemy import Column, Sequence, Integer, String, TIMESTAMP
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
