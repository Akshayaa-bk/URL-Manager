import mysql.connector

class SearchHandler:
    def __init__(self):
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Akshayaa_19",
            database="URLREC"
        )
        self.cursor = self.db.cursor()
        self.last_searched_keyword = None

    def search_urls(self, keyword):
        query = "SELECT url, url_savetime FROM URLs WHERE keywords LIKE %s ORDER BY url_savetime DESC"
        self.cursor.execute(query, (f"%{keyword}%",))
        results = self.cursor.fetchall()
        last_searched_keyword = keyword 
        print(last_searched_keyword) # Save the last searched keyword
        return results

    def get_last_searched_keyword(self):
        print(self.last_searched_keyword)
        return self.last_searched_keyword

    def close_connection(self):
        self.cursor.close()
        self.db.close()
