from DatabaseHandler import DatabaseHandler
from SearchHandler import SearchHandler
from RecommendUrls import Recommender

class URLManager:
    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.search_handler = SearchHandler()
        self.recommender = Recommender()

    def save_url_workflow(self):
        while True:
            url = input("Enter the URL (type 'back' to return to main menu): ").strip()
            if url.lower() == 'back':
                break
            try:
                if self.db_handler.url_exists(url):
                    print("URL already exists.")
                else:
                    self.db_handler.save_url(url)
                    content = self.db_handler.fetch_content(url)
                    if content == "Scraping not allowed by robots.txt":
                        print(content)
                    elif content.startswith("Failed to retrieve content"):
                        print(content)
                    else:
                        self.db_handler.save_content(url, content)
                        self.db_handler.keyword_summarize_text(url)  # Summarize the content and save summary to database
                        print("URL saved successfully")
            except Exception as e:
                print(f"An error occurred: {e}")

    def search_url_workflow(self):
        while True:
            keyword = input("Enter a keyword to search for (type 'back' to return to main menu): ").strip()
            if keyword.lower() == 'back':
                break
            try:
                results = self.search_handler.search_urls(keyword)
                if results:
                    print("URLs found:")
                    for url, savetime in results:
                        print(f"{savetime}: {url}")
                else:
                    print("No URLs found with the given keyword.")
            except Exception as e:
                print(f"An error occurred: {e}")

    def recommend_urls(self):
        try:
            recommendations = self.recommender.recommend_urls()
            if recommendations:
                print("Recommended URLs:")
                for url, savetime in recommendations:
                    print(f"{savetime}: {url}")
            else:
                print("No recommendations found.")
        except Exception as e:
            print(f"An error occurred while generating recommendations: {e}")

    def run(self):
        print("Welcome to the URL Manager")
        while True:
            action = input("Enter 'save' to save a URL, 'search' to search for URLs, 'recommend' for recommendations, or 'end' to end: ").lower()
            if action == 'end':
                print("Exiting the URL Manager. Goodbye!")
                break
            if action == 'save':
                self.save_url_workflow()
            elif action == 'search':
                self.search_url_workflow()
            elif action == 'recommend':
                self.recommend_urls()
            else:
                print("Invalid input. Please enter 'save', 'search', 'recommend', or 'end'.")

    def close(self):
        self.db_handler.close_connection()
        self.search_handler.close_connection()
        self.recommender.close_connection()


if __name__ == "__main__":
    url_manager = URLManager()
    try:
        url_manager.run()
    finally:
        url_manager.close()
