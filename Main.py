from DbConnection import Base, engine
from DatabaseHandler import DatabaseHandler
from SearchHandler import SearchHandler
from Recommender import Recommender
import time
import schedule
import threading

class URLManager:
    def __init__(self):
        # Initialize database connection and create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        self.db_handler = DatabaseHandler()
        self.search_handler = SearchHandler()
        self.recommender = Recommender()

        print("Welcome to the URL Manager")
        self.receiver_email = self.get_receiver_email()

        self.scheduler_thread = None  # Initialize scheduler thread
        self.stop_scheduler = False  # Flag to control scheduler loop

    def get_receiver_email(self):
        # Prompt the user to enter the receiver's email address
        receiver_email = input("Enter your email address: ").strip()
        return receiver_email

    def save_url_workflow(self):
        # Workflow to save a URL
        while True:
            url = input("Enter URL to save (type 'back' to return to main menu): ").strip()
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
                        self.db_handler.keyword_summarize_text(url)  # Save summary and keywords
                        print("URL saved successfully")
            except Exception as e:
                print(f"An error occurred: {e}")

    def search_url_workflow(self):
        # Workflow to search for URLs by keyword
        while True:
            keyword = input("Enter a keyword to search  (type 'back' to return to main menu): ").strip()
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
        # Generate URL recommendations based on the keywords from the last saved URL
        try:
            recommendations = self.recommender.recommend_urls()
            if recommendations:
                print("Recommended URLs:")
                for url, savetime in recommendations:
                    print(f"{savetime}: {url}")
            else:
                print("No recommendations found.")
        except Exception as e:
            print(f"An error occurred while fetching recommendations: {e}")

    def send_recommendation_email(self):
        # Send an email with the recommended URLs to the given email address
        try:
            self.recommender.send_recommendation_email(self.receiver_email)
            print(f"Check {self.receiver_email} for your today's recommendations .")
        except Exception as e:
            print(f"An error occurred while sending email: {e}")

    def schedule_recommendations(self):
       schedule.every().day.at("00:38").do(self.send_recommendation_email)
       

    def run_scheduler(self):
        # Run the scheduler to check and execute scheduled tasks
        while not self.stop_scheduler:
            schedule.run_pending()
            time.sleep(10)  
            

    def run(self):
        # Start the scheduler in a separate thread
        self.scheduler_thread = threading.Thread(target=self.run_scheduler)
        self.scheduler_thread.start()

        # Schedule email sending
       
        self.schedule_recommendations()

        while True:
            action = input("Enter 'save' to save a URL, 'search' to search for URLs, 'recommend' for recommendations, or 'end' to end: ").lower()
            if action == 'end':
                print("Closing ...")
                self.stop_scheduler = True  # Set flag to stop scheduler loop
                break
            elif action == 'save':
                self.save_url_workflow()
            elif action == 'search':
                self.search_url_workflow()
            elif action == 'recommend':
                self.recommend_urls()
            else:
                print("Invalid input. Please enter 'save', 'search', 'recommend', or 'end'.")

        # Ensure scheduler thread stops when main loop exits
        if self.scheduler_thread:
            self.scheduler_thread.join()

    def close(self):
        # Close all database connections
        self.db_handler.close_connection()
        self.search_handler.close_connection()
        self.recommender.close_connection()

if __name__ == "__main__":
    url_manager = URLManager()
    try:
        url_manager.run()
    finally:
        url_manager.close()
