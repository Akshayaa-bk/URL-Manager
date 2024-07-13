from Normalization import TextNormalization
from DbConnection import Base, engine, Session, URL
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

class DatabaseHandler:
    def __init__(self):
        # Initialize database connection and create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        self.Session = Session
        self.text_normalizer = TextNormalization()

    def url_exists(self, url):
        # Check if the URL already exists in the database
        session = self.Session()
        url_count = session.query(URL).filter(URL.url == url).count()
        session.close()
        return url_count > 0

    def save_url(self, url):
        # Save a new URL entry into the database
        session = self.Session()
        url_entry = URL(url=url, url_savetime=datetime.now())
        session.add(url_entry)
        session.commit()
        session.close()

    def can_fetch(self, url, user_agent='*'):
        # Check if scraping is allowed for the given URL based on robots.txt
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        rp = RobotFileParser()
        rp.set_url(base_url)
        rp.read()
        return rp.can_fetch(user_agent, url)

    def fetch_content(self, url):
        # Fetch the main content from the given URL if allowed by robots.txt
        if not self.can_fetch(url):
            return "Scraping not allowed by robots.txt"
        
        response = requests.get(url)
        if response.status_code != 200:
            return f"Failed to retrieve content: {response.status_code}"
        
        soup = BeautifulSoup(response.content, 'html.parser')
        main_content = soup.find('article') or soup.find('div', class_=lambda c: c and 'content' in c.split()) or soup.body
        return main_content.get_text() if main_content else "No main content found"

    def save_content(self, url, content):
        # Save fetched content to the database for the given URL
        session = self.Session()
        session.query(URL).filter(URL.url == url).update({URL.content: content})
        session.commit()
        session.close()

    def save_to_db(self, url, summary, keywords):
        # Save the summary and keywords to the database for the given URL
        session = self.Session()
        session.query(URL).filter(URL.url == url).update({URL.summary: summary, URL.keywords: keywords})
        session.commit()
        session.close()

    def fetch_content_from_db(self, url):
        # Retrieve the content from the database for the given URL
        session = self.Session()
        content = session.query(URL.content).filter(URL.url == url).scalar()
        session.close()
        return content
    
    def keyword_summarize_text(self, url):
        # Generate a summary and extract keywords from the content of the given URL
        content = self.fetch_content_from_db(url)
        s_content = self.text_normalizer.text_normalizer(content)
        
        # Use a pre-trained summarization model to generate summary
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        max_input_size = 1024
        num_chunks = (len(s_content) // max_input_size) + 1
        summary_chunks = []
        
        for i in range(num_chunks):
            start_idx = i * max_input_size
            end_idx = (i + 1) * max_input_size
            summary_chunk = summarizer(s_content[start_idx:end_idx], max_length=40, min_length=20, do_sample=False)[0]['summary_text']
            summary_chunks.append(summary_chunk)

        summary = ' '.join(summary_chunks)

        # Extract keywords using TF-IDF vectorizer
        vectorizer = TfidfVectorizer(stop_words='english', max_features=20)
        X = vectorizer.fit_transform([s_content])
        keywords = vectorizer.get_feature_names_out()
        
        # Save the summary and keywords to the database
        self.save_to_db(url, summary, ', '.join(keywords))

    def close_connection(self):
        # Close the database connection
        self.Session().close()
