import numpy as np
import pandas as pd
from flask import render_template, request
import pickle
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app import app

# Load the movie data
movie_data = pd.read_csv('../main_data.csv')

# Clean movie titles for better matching
movie_data['movie_title'] = movie_data['movie_title'].apply(lambda x: x.strip() if isinstance(x, str) else x)

# Load the NLP model (Naive Bayes Classifier) and vectorizer for sentiment analysis
sentiment_model = pickle.load(open('nlp_model.pkl', 'rb'))
vectorizer = pickle.load(open('tranform.pkl', 'rb'))

# Create a TF-IDF matrix for movie recommendations
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movie_data['comb'].fillna(''))
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Helper function to get movie recommendations
def get_recommendations(title, cosine_sim=cosine_sim):
    # Get the index of the movie that matches the title
    title = title.lower().strip()
    indices = movie_data.index[movie_data['movie_title'].str.lower() == title].tolist()
    
    if not indices:
        # Try to find partial matches
        indices = movie_data.index[movie_data['movie_title'].str.lower().str.contains(title)].tolist()
        
    if not indices:
        return []
    
    # Get the index of the first matching movie
    idx = indices[0]
    
    # Get the pairwise similarity scores of all movies with that movie
    sim_scores = list(enumerate(cosine_sim[idx]))
    
    # Sort the movies based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Get the scores of the 10 most similar movies (excluding the movie itself)
    sim_scores = sim_scores[1:11]
    
    # Get the movie indices
    movie_indices = [i[0] for i in sim_scores]
    
    # Return the top 10 most similar movies
    return movie_data.iloc[movie_indices][['movie_title', 'director_name', 'actor_1_name', 'actor_2_name', 'actor_3_name', 'genres']].to_dict('records')

# Helper function for sentiment analysis
def sentiment_analysis(review):
    review = re.sub('[^a-zA-Z]', ' ', review)
    review = review.lower()
    review = review.split()
    review = ' '.join(review)
    
    # Transform the review using the loaded vectorizer
    review_vector = vectorizer.transform([review])
    
    # Predict the sentiment using the loaded model
    prediction = sentiment_model.predict(review_vector)
    
    return "Positive" if prediction[0] == 1 else "Negative"

@app.route('/')
def home():
    # Get a list of movie titles for the dropdown and convert them to uppercase
    movie_titles = sorted(movie_data['movie_title'].tolist())
    movie_titles = [title.upper() for title in movie_titles]
    return render_template('index.html', movie_titles=movie_titles)

@app.route('/recommend', methods=['POST'])
def recommend():
    movie_title = request.form['movie_title']
    recommendations = get_recommendations(movie_title)
    
    if not recommendations:
        return render_template('recommend.html', 
                              movie_title=movie_title, 
                              recommendations=[], 
                              no_results=True)
    
    return render_template('recommend.html', 
                          movie_title=movie_title, 
                          recommendations=recommendations, 
                          no_results=False)

@app.route('/movie/<movie_title>')
def movie_details(movie_title):
    # Convert URL-formatted title back to normal
    movie_title = movie_title.replace('_', ' ')
    
    # Get movie details from the dataframe
    movie_details = movie_data[movie_data['movie_title'].str.lower() == movie_title.lower()]
    
    if movie_details.empty:
        return render_template('movie_details.html', movie=None, not_found=True)
    
    movie = movie_details.iloc[0].to_dict()
    
    return render_template('movie_details.html', movie=movie, not_found=False)

@app.route('/review', methods=['POST'])
def review():
    user_review = request.form['review']
    movie_title = request.form['movie_title']
    sentiment = sentiment_analysis(user_review)
    
    return render_template('review.html', 
                          movie_title=movie_title, 
                          review=user_review, 
                          sentiment=sentiment) 