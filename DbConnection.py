from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Defining the database connection URL
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:Akshayaa_19@localhost/URLREC"

# SQLAlchemy engine creation
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SQLAlchemy Base object definition
Base = declarative_base()

# URL model definition
class URL(Base):
    __tablename__ = 'URLs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(255), unique=True, nullable=False)
    content = Column(Text)
    summary = Column(Text)
    keywords = Column(Text)
    url_savetime = Column(DateTime)

    def __repr__(self):
        return f"<URL(url='{self.url}', url_savetime='{self.url_savetime}')>"

# sessionmaker to manage sessions
Session = sessionmaker(bind=engine)
