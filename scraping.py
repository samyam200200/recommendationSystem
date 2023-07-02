# Scraping data from the goodreads website using BeautifulSoup
import requests
import bs4
import json
import pandas as pd
import re

# Genres list is found in the goodreads website - these are the main genres
genres=[
"Art",
"Biography",
"Business",
"Children's",
"Christian",
"Classics",
"Comics",
"Cookbooks",
"Ebooks",
"Fantasy",
"Fiction",
"Graphic Novels",
"Historical Fiction",
"History",
"Horror",
"Memoir",
"Music",
"Mystery",
"Nonfiction",
"Poetry",
"Psychology",
"Romance",
"Science",
"Science Fiction",
"Self Help",
"Sports",
"Thriller",
"Travel",
"Young Adult",]
URL = "https://www.goodreads.com/shelf/show/"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
book_reviews = pd.DataFrame()
done_list=[]
for genre in genres:
    if genre not in done_list:
        genre_copy=genre
        genre_dataframe=pd.DataFrame()
        # We will be scraping 50 books from each genre
        #we will get book name, author, rating, number of ratings, number of reviews, and the link to the book
        book_titles_list = []
        book_authors_list = []
        book_ratings_list = []
        book_description_list = []
        book_genre_list = []
        # If the genre name contains a space, replace it with a hyphen in the URL
        if " " in genre:
            genre=re.sub(" ", "-", genre)
        response=requests.get(URL+"/"+genre, headers=headers)
        soup = bs4.BeautifulSoup(response.content, 'html.parser')
        soup_pretty = bs4.BeautifulSoup(soup.prettify(), 'html.parser')
        book_titles=soup_pretty.find_all("a", class_="bookTitle")
        for book_title in book_titles:
            book_title=re.sub(r'\([^)]*\)', '', book_title.text)
            book_titles_list.append(book_title)
        author_names=soup_pretty.find_all("span", itemprop="author")
        for author_name in author_names:
            author_name=re.sub(r'\([^)]*\)', '', author_name.text)
            book_authors_list.append(author_name)
        book_ratings=soup_pretty.find_all("span", class_="smallText")
        for book_rating in book_ratings:
            if book_rating.text.strip().startswith("avg rating"):
                book_ratings_list.append(book_rating.text.strip())
        book_link=soup_pretty.find_all("a", class_="bookTitle")
        ratings_text_list = []
        indi_ratings_list = []
        rating_creator_list = []

        for book in book_link:
            #using the link we will get the description of the book, the genre tags for each book, the number of ratings, and 30 reviews for each book
            print("https://www.goodreads.com"+book["href"])
            one_book=requests.get("https://www.goodreads.com"+book["href"], headers=headers)
            soup_book = bs4.BeautifulSoup(one_book.content, 'html.parser')
            soup_book_pretty = bs4.BeautifulSoup(soup_book.prettify(), 'html.parser')
            # Find the script containing the book data
            script = soup_book_pretty.find('script', id="__NEXT_DATA__", type="application/json")
            while script is None:
                # Retry until the script is found
                one_book=requests.get("https://www.goodreads.com"+book["href"], headers=headers)
                soup_book = bs4.BeautifulSoup(one_book.content, 'html.parser')
                soup_book_pretty = bs4.BeautifulSoup(soup_book.prettify(), 'html.parser')
                script = soup_book_pretty.find('script', id="__NEXT_DATA__", type="application/json")

            json_data = json.loads(script.contents[0])["props"]["pageProps"]["apolloState"]
            while json_data=={}:
                # Retry until the JSON data is populated
                one_book=requests.get("https://www.goodreads.com"+book["href"], headers=headers)
                soup_book = bs4.BeautifulSoup(one_book.content, 'html.parser')
                script = soup_book.find('script', id="__NEXT_DATA__", type="application/json")
                json_data = json.loads(script.contents[0])["props"]["pageProps"]["apolloState"]

            rating_points=[]
            ratings_text=[]
            rating_creator=[]
            for item in json_data.keys():
                if item.startswith("Book:"):
                    if "description" in json_data[item]:
                        if json_data[item]["description"] is not None:
                            book_description_list.append(json_data[item]["description"])
                        else:
                            book_description_list.append("")
                    else:
                        book_description_list.append("")
                    if json_data[item]["bookGenres"] is not None:
                        book_genre_list.append([item["genre"]["name"] for item in json_data[item]["bookGenres"]])
                    else:
                        book_genre_list.append([])
                if item.startswith("Review:"):
                    ratings_text.append(json_data[item]["text"])
                    rating_points.append(json_data[item]["rating"])
                    rating_creator.append(json_data[item]["creator"]["__ref"])
            ratings_text_list.append(ratings_text)
            indi_ratings_list.append(rating_points)
            rating_creator_list.append(rating_creator)
        genre_dataframe["book_title"]=book_titles_list
        genre_dataframe["book_author"]=book_authors_list
        genre_dataframe["book_rating"]=book_ratings_list
        genre_dataframe["book_description"]=book_description_list
        genre_dataframe["book_genre"]=book_genre_list
        genre_dataframe["ratings_text"]=ratings_text_list
        genre_dataframe["indi_ratings"]=indi_ratings_list
        genre_dataframe["rating_creator"]=rating_creator_list
        genre_dataframe["genre"]=genre
        book_reviews=pd.concat([book_reviews, genre_dataframe], ignore_index=True)
        done_list.append(genre_copy)
#the dataframe will be saved as book_reviews.pkl in the data folder
book_reviews.to_pickle("book_reviwes.pkl")
