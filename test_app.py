import pytest
from app.routes import app
from unittest.mock import patch

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200

@patch('app.routes.get_recommendations')
def test_recommend(mock_get_recommendations, client):
    mock_get_recommendations.return_value = [
        {'movie_title': 'Inception', 'director_name': 'Nolan', 'actor_1_name': 'Leo',
         'actor_2_name': 'Joseph', 'actor_3_name': 'Elliot', 'genres': 'Action'}
    ]
    response = client.post('/recommend', data={'movie_title': 'Inception'})
    assert response.status_code == 200

@patch('app.routes.movie_data')
def test_movie_details(mock_movie_data, client):
    mock_movie_data.__getitem__.return_value.str.lower.__eq__.return_value = [True]
    mock_movie_data.__getitem__.return_value.empty = False
    mock_movie_data.__getitem__.return_value.iloc.__getitem__.return_value.to_dict.return_value = {
        'movie_title': 'Inception', 'director_name': 'Nolan'
    }
    response = client.get('/movie/Inception')
    assert response.status_code == 200

@patch('app.routes.sentiment_analysis')
def test_review(mock_sentiment, client):
    mock_sentiment.return_value = 'Positive'
    response = client.post('/review', data={'review': 'Great movie!', 'movie_title': 'Inception'})
    assert response.status_code == 200
