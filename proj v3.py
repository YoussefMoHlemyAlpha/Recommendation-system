import feedparser
import re
from translate import Translator
from gtts import gTTS
import time
from pytube import YouTube
from pytube import Search
import pygame
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

def get_news_feeds(feedURL):
    feeds = feedparser.parse(feedURL)
    news_list = []
    for line in feeds.entries:
        news_list.append({
            'title': line.title,
            'description': line.description
        })
    return news_list

def recommend_news(user_input, news_list):
    # Combine title and description into a single string for each news item
    news_corpus = [f"{item['title']} {item['description']}" for item in news_list]

    # Create a TF-IDF vectorizer
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')

    # Fit and transform the corpus
    tfidf_matrix = tfidf_vectorizer.fit_transform(news_corpus)

    # Transform user input
    user_tfidf = tfidf_vectorizer.transform([user_input])

    # Calculate cosine similarity between user input and news items
    cosine_similarities = linear_kernel(user_tfidf, tfidf_matrix).flatten()

    # Get indices of top recommendations
    top_indices = cosine_similarities.argsort()[:-6:-1]

    # Return the recommended news items
    recommendations = [news_list[i] for i in top_indices]
    return recommendations

def download_video(youtube_url, output_path):
    try:
        youtube_object = YouTube(youtube_url)
        youtube_stream = youtube_object.streams.get_highest_resolution()
        if youtube_stream:
            youtube_stream.download(output_path)
            print("Video downloaded successfully.")
        else:
            print("No suitable streams found for the video.")
    except Exception as e:
        print(f"Error downloading video: {e}")

def NewsDownloader(lang, feedURL, WordToSearch):
    pygame.mixer.init()
    translator = Translator(to_lang=lang)

    feeds = feedparser.parse(feedURL)

    for line in feeds.entries:
        if re.search(WordToSearch, line.description, re.IGNORECASE) or re.search(WordToSearch, line.title, re.IGNORECASE):
            # Translate and play title
            translated_title = translator.translate(line.title)
            title_tts = gTTS(translated_title, lang=lang)
            title_tts_file = f"{line.title[:10]}_title.mp3"  # Unique file name
            title_tts.save(title_tts_file)
            print("Newspaper title:",line.title)
            pygame.mixer.music.load(title_tts_file)
            pygame.mixer.music.play()
            time.sleep(10)

            # Translate and play description
            translated_desc = translator.translate(line.description)
            desc_tts = gTTS(translated_desc, lang=lang)
            desc_tts_file = f"{line.title[:10]}_description.mp3"  # Unique file name
            desc_tts.save(desc_tts_file)
            print("Newspaper description:\n",line.description)
            pygame.mixer.music.load(desc_tts_file)
            pygame.mixer.music.play()
            time.sleep(10)

            # Search for the title on YouTube
            search_query = line.title
            search_results = Search(search_query)

            if search_results.results:
                first_video = search_results.results[0]
                print("Title:", first_video.title)
                print("URL:", first_video.watch_url)

                # Download video
                output_path = f"{line.title[:10]}_video.mp4"
                download_video(first_video.watch_url, output_path)

            else:
                print("No videos found for the search query.")

            print("=" * 60)
            
if __name__ == "__main__":
 
    feed_urls = {
        '1': "https://feeds.skynews.com/feeds/rss/home.xml",
        '2': "https://feeds.skynews.com/feeds/rss/uk.xml",
        '3': "https://feeds.skynews.com/feeds/rss/world.xml",
        '4': "https://feeds.skynews.com/feeds/rss/us.xml",
        '5': "https://feeds.skynews.com/feeds/rss/business.xml",
        '6': "https://feeds.skynews.com/feeds/rss/politics.xml",
        '7': "https://feeds.skynews.com/feeds/rss/technology.xml",
        '8': "https://feeds.skynews.com/feeds/rss/entertainment.xml",
        '9': "https://feeds.skynews.com/feeds/rss/strange.xml",
    }
    
    while True:
        print("Categories:")
        print("1. Home")
        print("2. UK")
        print("3. World")
        print("4. US")
        print("5. Business")
        print("6. Politics")
        print("7. Technology")
        print("8. Entertainment")
        print("9. Strange")
        print("0. Exit")
        
        option = input("Enter category to search about using feeds.skynews.com: ")

        if option == '0':
            break  # Exit the loop

        feed_url = feed_urls.get(option)

        if feed_url:
            user_input = input("Enter keywords to search for: ")

            news_list = get_news_feeds(feed_url)
            recommendations = recommend_news(user_input, news_list)

            print("\nTop 5 Recommended News:")
            for i, news in enumerate(recommendations, 1):
                print(f"{i}. Title: {news['title']}")

            choose = input("Enter a keyword from titles to search for: ")
            NewsDownloader("ar", feed_url, choose)
        else:
            print("Enter a valid number, please try again")