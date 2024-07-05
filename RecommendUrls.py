import mysql.connector

class Recommender:
    def __init__(self):
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Akshayaa_19",
            database="URLREC"
        )
        self.cursor = self.db.cursor()

    def get_keywords_from_last_saved_url(self):
        query = "SELECT keywords FROM URLs ORDER BY url_savetime DESC LIMIT 1"
        self.cursor.execute(query)
        results = self.cursor.fetchall()

        if results:
            keywords_str = results[0][0]
            if keywords_str:
                return keywords_str.split(', ')
        return []

    def get_urls_by_keywords(self, keywords):
        keyword_conditions = ' OR '.join(['keywords LIKE %s'] * len(keywords))
        query = f"SELECT url, url_savetime FROM URLs WHERE {keyword_conditions} ORDER BY url_savetime DESC LIMIT 5"
        params = tuple(f"%{keyword}%" for keyword in keywords)
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def recommend_urls(self):
        keywords = self.get_keywords_from_last_saved_url()
        related_urls = self.get_urls_by_keywords(keywords)
        return related_urls

    def close_connection(self):
        self.cursor.close()
        self.db.close()
