import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture(scope='module')
def mock_app():
    with patch('app.routes.pd.read_csv') as mock_read_csv, \
         patch('app.routes.pickle.load') as mock_pickle_load:
        
        # Mock minimal movie_data DataFrame
        import pandas as pd
        from pandas import DataFrame
        
        data = {
            'movie_title': ['Inception', 'Interstellar', 'Dunkirk'],
            'director_name': ['Christopher Nolan', 'Christopher Nolan', 'Christopher Nolan'],
            'actor_1_name': ['Leonardo DiCaprio', 'Matthew McConaughey', 'Fionn Whitehead'],
            'actor_2_name': ['Joseph Gordon-Levitt', 'Anne Hathaway', 'Tom Hardy'],
            'actor_3_name': ['Ellen Page', 'Jessica Chastain', 'Harry Styles'],
            'genres': ['Action|Sci-Fi', 'Adventure|Drama', 'War|Drama'],
            'comb': ['inception action sci-fi', 'interstellar adventure drama', 'dunkirk war drama']
        }
        mock_df = DataFrame(data)
        mock_read_csv.return_value = mock_df
        
        # Mock the pickle.load to return a mock model with predict method
        mock_model = MagicMock()
        mock_model.predict.return_value = [1]  # Always positive sentiment
        mock_pickle_load.return_value = mock_model
        
        # Import app after mocking
        from app.routes import app
        yield app

@pytest.fixture
def client(mock_app):
    mock_app.config['TESTING'] = True
    with mock_app.test_client() as client:
        yield client

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    # Should contain some movie title (uppercase)
    assert b'INCEPTION' in response.data or b'INTERSTELLAR' in response.data

def test_recommend_valid_movie(client):
    response = client.post('/recommend', data={'movie_title': 'Inception'})
    assert response.status_code == 200
    assert b'Christopher Nolan' in response.data  # director's name present in recommendations

def test_recommend_invalid_movie(client):
    response = client.post('/recommend', data={'movie_title': 'NonExistingMovie'})
    assert response.status_code == 200
    # no_results flag should be True, so check some text related to no results
    assert b'No recommendations found' in response.data or b'no_results' in response.data

def test_movie_details_found(client):
    response = client.get('/movie/Inception')
    assert response.status_code == 200
    assert b'Inception' in response.data or b'Christopher Nolan' in response.data

def test_movie_details_not_found(client):
    response = client.get('/movie/UnknownMovie')
    assert response.status_code == 200
    assert b'not found' in response.data.lower() or b'not_found' in response.data

def test_review_sentiment(client):
    response = client.post('/review', data={'movie_title': 'Inception', 'review': 'This movie was amazing!'})
    assert response.status_code == 200
    assert b'Positive' in response.data  # our mock model always returns positive
