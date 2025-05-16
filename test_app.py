import pytest
from unittest.mock import patch, MagicMock
from app.routes import app
import pandas as pd

# Sample dummy movie data
dummy_movie_data = pd.DataFrame({
    'movie_title': ['Movie1', 'Movie2'],
    'comb': ['action thriller', 'comedy drama'],
    'director_name': ['Dir1', 'Dir2'],
    'actor_1_name': ['Actor1', 'Actor2'],
    'actor_2_name': ['Actor3', 'Actor4'],
    'actor_3_name': ['Actor5', 'Actor6'],
    'genres': ['Action|Thriller', 'Comedy']
})

# Dummy sentiment model
dummy_sentiment_model = MagicMock()
dummy_sentiment_model.predict.return_value = [1]  # Always "Positive"

# Dummy vectorizer
dummy_vectorizer = MagicMock()
dummy_vectorizer.transform.return_value = [[0.1, 0.9]]

@pytest.fixture
def client():
    with patch('app.routes.pd.read_csv', return_value=dummy_movie_data), \
         patch('app.routes.pickle.load', side_effect=[dummy_sentiment_model, dummy_vectorizer]), \
         patch('app.routes.TfidfVectorizer.fit_transform', return_value=[[1, 0.9], [0.9, 1]]), \
         patch('app.routes.cosine_similarity', return_value=[[1, 0.9], [0.9, 1]]):

        app.testing = True
        with app.test_client() as client:
            yield client
def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'MOVIE1' in response.data

def test_recommend_valid(client):
    response = client.post('/recommend', data={'movie_title': 'Movie1'})
    assert response.status_code == 200
    assert b'Movie2' in response.data

def test_recommend_invalid(client):
    response = client.post('/recommend', data={'movie_title': 'Unknown'})
    assert response.status_code == 200
    assert b'No results' in response.data or b'no recommendations' in response.data.lower()

def test_review_sentiment(client):
    response = client.post('/review', data={
        'movie_title': 'Movie1',
        'review': 'Great movie!'
    })
    assert response.status_code == 200
    assert b'POSITIVE REVIEW' in response.data
