from sqlalchemy.orm import sessionmaker
from DbConnection import Base, engine, Session, URL

class SearchHandler:
    def __init__(self):
        # Initialize database connection and create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        self.Session = Session

    def search_urls(self, keyword):
        # Search for URLs in the database that contain the given keyword in their keywords
        session = self.Session()
        # Perform a case-insensitive search for the keyword in the 'keywords' field and order results by save time in descending order
        results = session.query(URL.url, URL.url_savetime).filter(URL.keywords.like(f'%{keyword}%')).order_by(URL.url_savetime.desc()).all()
        session.close()
        return results

    def close_connection(self):
        # Close the database connection
        self.Session().close()
