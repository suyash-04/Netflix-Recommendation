import os
import numpy as np
import pandas as pd
from flask import render_template, request
import pickle
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app import app

# Globals initialized as None
movie_data = None
sentiment_model = None
vectorizer = None
cosine_sim = None

def load_resources():
    global movie_data, sentiment_model, vectorizer, cosine_sim
    
    if movie_data is None:
         csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'main_data.csv')
        movie_data = pd.read_csv(csv_path)
        movie_data['movie_title'] = movie_data['movie_title'].apply(lambda x: x.strip() if isinstance(x, str) else x)
    
    if sentiment_model is None:
        sentiment_model = pickle.load(open('nlp_model.pkl', 'rb'))
    
    if vectorizer is None:
        vectorizer = pickle.load(open('tranform.pkl', 'rb'))
    
    if cosine_sim is None:
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(movie_data['comb'].fillna(''))
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

def get_recommendations(title):
    load_resources()  # Ensure resources are loaded
    
    global movie_data, cosine_sim
    title = title.lower().strip()
    indices = movie_data.index[movie_data['movie_title'].str.lower() == title].tolist()
    
    if not indices:
        indices = movie_data.index[movie_data['movie_title'].str.lower().str.contains(title)].tolist()
    
    if not indices:
        return []
    
    idx = indices[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores]
    
    return movie_data.iloc[movie_indices][['movie_title', 'director_name', 'actor_1_name', 'actor_2_name', 'actor_3_name', 'genres']].to_dict('records')

def sentiment_analysis(review):
    load_resources()  # Ensure model and vectorizer loaded
    
    global sentiment_model, vectorizer
    review = re.sub('[^a-zA-Z]', ' ', review)
    review = review.lower()
    review = review.split()
    review = ' '.join(review)
    review_vector = vectorizer.transform([review])
    prediction = sentiment_model.predict(review_vector)
    return "Positive" if prediction[0] == 1 else "Negative"

@app.route('/')
def home():
    load_resources()  # Ensure movie data loaded
    
    global movie_data
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
    load_resources()  # Ensure movie data loaded
    
    global movie_data
    movie_title = movie_title.replace('_', ' ')
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
