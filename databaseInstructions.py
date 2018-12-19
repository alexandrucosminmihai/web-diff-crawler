from sqlalchemy import create_engine, Column, Sequence, Integer, String, TIMESTAMP
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base

import datetime

# Underlying SQLAlchemy Engine object for the database connection
# Insert DB credentials here
engine = create_engine('postgresql://webdiffcrawler:somepassword@localhost/webdiffcrawler', echo = True)

# Session factory class. Will be used to create session objects that are needed for communicating with the database
Session = sessionmaker(bind=engine)

# Declarative base
Base = declarative_base()

# Mapped Class for the 'crawlingrules' table
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

if __name__ == "__main__":
    session = Session()


    print("Before adding the new database entry:")
    # Query all the entries in a table
    print(session.query(Crawlingrules).order_by(Crawlingrules.id_crawlingrules).all())

    # Add a new row to the table
    newCrawlingrule = Crawlingrules(address="https://clnr.ro/", selectionrule="div.logo_container",
                                  lastmodifytime=datetime.datetime.now(), contributor="testUser", content="<div></div>")
    session.add(newCrawlingrule)
    session.commit()

    print("After adding the new database entry:")
    print(session.query(Crawlingrules).order_by(Crawlingrules.id_crawlingrules).all())

    # Delete a row from the table
    crawledpageToDelete = session.query(Crawlingrules).\
        filter_by(address="https://clnr.ro/").order_by(Crawlingrules.id_crawlingrules.desc()).first()
    session.delete(crawledpageToDelete)
    session.commit()

    print("After deleting the new database entry:")
    print(session.query(Crawlingrules).order_by(Crawlingrules.id_crawlingrules).all())

    session.close()
