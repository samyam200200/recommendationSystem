import pandas as pd
import numpy as np
import re
from fuzzywuzzy import process
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.metrics.pairwise import cosine_similarity

# Loads a pandas DataFrame from a pickle file containing book reviews. For scraping view scraping.py
book_reviews=pd.read_pickle("book_reviwes.pkl")

def clean_text(text):
    """
    Cleans the given text by removing newlines, carriage returns, tabs, HTML tags, and leading/trailing white spaces.

    Args:
        text (str): The text to be cleaned.

    Returns:
        str: The cleaned text.
    """
    text=re.sub(r'\n', '', text)
    text=re.sub(r'\r', '', text)
    text=re.sub(r'\t', '', text)
    text=re.sub(r'<.*?>', '', text)
    text=text.strip()
    return text

# Clean the 'book_title' column by applying the 'clean_text' function to each element
book_reviews["book_title"] = book_reviews["book_title"].apply(clean_text)

# Clean the 'book_author' column by applying the 'clean_text' function to each element
book_reviews["book_author"] = book_reviews["book_author"].apply(clean_text)

# Clean the 'book_description' column by applying the 'clean_text' function to each element
book_reviews["book_description"] = book_reviews["book_description"].apply(clean_text)

# Extract the average book rating from the 'book_rating' column and convert it to a float
book_reviews["avg_book_rating"] = book_reviews["book_rating"].str.split(" ", expand=True)[2].astype(float)

# Extract the number of book ratings from the 'book_rating' column, remove commas, and convert it to an integer
book_reviews["num_book_ratings"] = book_reviews["book_rating"].str.split(" ", expand=True)[19].str.replace(",", "").astype(int)

# Extract the year of publication from the 'book_rating' column
book_reviews["year_published"] = book_reviews["book_rating"].str.split(" ", expand=True)[39]



cleaned_list = []
# Iterate over each element in the 'ratings_text' column converted to a list
for i in book_reviews["ratings_text"].to_list():
    list_of_reviews = []
    for j in i:
        # Clean the review by applying the 'clean_text' function
        list_of_reviews.append(clean_text(j))
    cleaned_list.append(list_of_reviews)

# Update the 'ratings_text' column with the cleaned reviews
book_reviews["ratings_text"] = cleaned_list

all_users=[]
for user in book_reviews["rating_creator"].to_list():
    user_list=[]
    for i in range(len(user)):
        user_list.append(user[i].split(":")[1])
    all_users.append(user_list)
book_reviews["rating_creator"]=all_users

genre_list=[]
for i in book_reviews["book_genre"].to_list():
    for j in i:
        if j not in genre_list:
            genre_list.append(j)

author_list=[]
for i in book_reviews["book_author"].to_list():
    if i not in author_list:
        author_list.append(i)

def get_book_preferences():
    """
    Prompts the user to provide their book preferences and returns a dictionary containing the preferences.

    Returns:
        dict: A dictionary containing the user's book preferences.

    Example:
        >>> preferences = get_book_preferences()
        Welcome! Please provide your book preferences:
        Preferred genre separated by comma: Mystery, Thriller, Romance
        Preferred author separated by comma: Agatha Christie, Stephen King
        Preferred average rating (1-5): 4.5
        >>> print(preferences)
        {'genre': ['Mystery', 'Thriller', 'Romance'],
         'author': ['Agatha Christie', 'Stephen King'],
         'avg_book_rating': 4.5}
    """
    preferences = {}
    print("Welcome! Please provide your book preferences:")
    preferences['genre'] = input("Preferred genre separated by comma: ")
    #genre search
    
    preferences_genre=[i.strip() for i in preferences['genre'].split(",")]
    for i in preferences_genre:
        genre_match=process.extract(i, genre_list, limit=1)
        if genre_match[0][1]>70:
            preferences_genre[preferences_genre.index(i)]=genre_match[0][0]
    preferences['genre']=preferences_genre
    preferences['author'] = input("Preferred author separated by comma: ")
    preferences_author=[i.strip() for i in preferences['author'].split(",")]
    for i in preferences_author:
        author_match=process.extract(i, author_list, limit=1)
        if author_match[0][1]>70:
            preferences_author[preferences_author.index(i)]=author_match[0][0]
    preferences['author']=preferences_author

    while True:
        try:
            preferences['avg_book_rating'] = float(input("Preferred average rating (1-5): "))
            break
        except ValueError:
            print("Please enter a number")
    return preferences

user_preferences = get_book_preferences()

tfidf = TfidfVectorizer(stop_words='english')
book_reviews['book_description'] = book_reviews['book_description'].fillna('')
tfidf_matrix = tfidf.fit_transform(book_reviews['book_description'])

cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

def find_max_match_genre(user_preferences, number_of_books=5):
    """
    Finds and returns a filtered DataFrame of book reviews based on the user's genre preferences and average rating threshold.
    Used for content based and hybrid recommendation systems.

    Args:
        user_preferences (dict): A dictionary containing the user's book preferences, including 'genre' and 'avg_book_rating'.
        number_of_books (int, optional): The maximum number of books to return + prefrence given to specific author. Defaults to 5.

    Returns:
        pandas.DataFrame: A filtered DataFrame of book reviews based on the user's preferences.
    """
    genre_match=[]
    for i in range(len(book_reviews)):
        if book_reviews["book_genre"][i] not in genre_match:
            genre_match.append(len(set(user_preferences["genre"]).intersection(set(book_reviews["book_genre"][i]))))
    book_reviews["genre_match"]=genre_match
    book_reviews_filtered=book_reviews[book_reviews["avg_book_rating"]>=user_preferences["avg_book_rating"]]
    book_reviews_filtered=book_reviews_filtered.sort_values(by="genre_match", ascending=False)
    book_reviews_filtered=book_reviews_filtered.head(number_of_books)
    book_reviews_author=book_reviews["book_author"].isin(user_preferences["author"])
    book_reviews_filtered=pd.concat([book_reviews_filtered, book_reviews[book_reviews_author]])
    return book_reviews_filtered

content_filtered_books =find_max_match_genre(user_preferences)

def find_similar_books(content_filtered_books_df, number_of_books=3):
    """
    Finds and returns a DataFrame of similar books based on the content-filtered books.

    Args:
        content_filtered_books_df (pandas.DataFrame): A DataFrame containing content-filtered books.
        number_of_books (int, optional): The number of similar books to return. Defaults to 3.

    Returns:
        pandas.DataFrame: A DataFrame of similar books based on the content-filtered books.
    """
    return_dataframe=pd.DataFrame()
    similar_books = []
    for i in range(len(content_filtered_books_df)):
        similar_books.append(content_filtered_books_df.index[i])
    sim_scores = list(enumerate(cosine_similarity(tfidf_matrix[similar_books], tfidf_matrix)))
    for i in sim_scores:
        return_dataframe=pd.concat([return_dataframe, book_reviews.iloc[np.argsort(i[1])[::-1][1:number_of_books+1]]])
    return_dataframe=return_dataframe.drop_duplicates(subset=['book_title'])
    return return_dataframe

similar_books = find_similar_books(content_filtered_books)

if __name__ == "__main__":
    print("Here are your recommendations:")
    print(similar_books['book_title'].to_string(index=False))
