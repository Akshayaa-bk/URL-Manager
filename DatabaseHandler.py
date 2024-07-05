from Normalization import TextNormalization
import mysql.connector
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer


class DatabaseHandler:
    def __init__(self):
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Akshayaa_19",
            database="URLREC"
        )
        self.cursor = self.db.cursor()
        self.text_normalizer = TextNormalization()

        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS URLs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                url VARCHAR(255) NOT NULL UNIQUE,
                content TEXT,
                summary TEXT,
                keywords TEXT,
                url_savetime DATETIME
            )
        """)
        self.db.commit()

    def url_exists(self, url):
        self.cursor.execute("SELECT COUNT(*) FROM URLs WHERE url = %s", (url,))
        exists = self.cursor.fetchone()[0] > 0
        return exists

    def save_url(self, url):
        url_savetime = datetime.now()
        self.cursor.execute("INSERT INTO URLs (url, url_savetime) VALUES (%s, %s)", (url, url_savetime))
        self.db.commit()

    def can_fetch(self, url, user_agent='*'):
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        rp = RobotFileParser()
        rp.set_url(base_url)
        rp.read()
        return rp.can_fetch(user_agent, url)

    def fetch_content(self, url):
        if not self.can_fetch(url):
            return "Scraping not allowed by robots.txt"
        
        response = requests.get(url)
        if response.status_code != 200:
            return f"Failed to retrieve content: {response.status_code}"
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Attempt to find main content in common elements
        main_content = None
        
        # Look for <article> tag
        main_content = soup.find('article')
        
        # If <article> not found, look for <div> with class attribute starts with 'content'
        if not main_content:
            main_content = soup.find('div', class_=lambda c: c and 'content' in c.split())
        
        # Fallback to <body> if main content not found in specific elements
        if not main_content:
            main_content = soup.body
        
        if main_content:
            body_content = main_content.get_text()
        else:
            body_content = "No main content found"
        
        return body_content

    def save_content(self, url, content):
        self.cursor.execute("UPDATE URLs SET content = %s WHERE url = %s", (content, url))
        self.db.commit()

    def fetch_content_from_db(self, url):
        self.cursor.execute("SELECT content FROM URLs WHERE url = %s", (url,))
        content = self.cursor.fetchone()[0]
        return content

    def save_to_db(self, url, summary, keywords):
        self.cursor.execute("UPDATE URLs SET summary = %s, keywords = %s WHERE url = %s", (summary, keywords, url))
        self.db.commit()

    def keyword_summarize_text(self, url):
        content = self.fetch_content_from_db(url)
        s_content = self.text_normalizer.text_normalizer(content)
        
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        max_input_size = 1024
        num_chunks = (len(s_content) // max_input_size) + 1
        summary_chunks = []
        
        for i in range(num_chunks):
            start_idx = i * max_input_size
            end_idx = (i + 1) * max_input_size
            summary_chunk = summarizer(s_content[start_idx:end_idx], max_length=40, min_length=20, do_sample=False)[0]['summary_text']
            summary_chunks.append(summary_chunk)

        # Combine all summary chunks into one summary
        summary = ' '.join(summary_chunks)

        vectorizer = TfidfVectorizer(stop_words='english', max_features=20)
        X = vectorizer.fit_transform([s_content])
        keywords = vectorizer.get_feature_names_out()
        
        self.save_to_db(url, summary, ', '.join(keywords))

    def close_connection(self):
        self.cursor.close()
        self.db.close()
    