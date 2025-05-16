import pytest
from unittest.mock import patch, MagicMock
from app import create_app

import pandas as pd

# Sample dummy data to return instead of reading main_data.csv
dummy_movie_data = pd.DataFrame({
    'title': ['Movie1', 'Movie2'],
    'genres': ['Action|Thriller', 'Comedy'],
})

# Sample dummy pickle model
dummy_model = MagicMock()
dummy_model.predict = MagicMock(return_value=['Movie2'])

@pytest.fixture(scope='module')
def mock_app():
    # Patch pd.read_csv and pickle.load where they are imported (app.routes)
    with patch('app.routes.pd.read_csv', return_value=dummy_movie_data) as mock_read_csv, \
         patch('app.routes.pickle.load', return_value=dummy_model) as mock_pickle_load:
        app = create_app()
        app.testing = True
        yield app

def test_recommend_valid_movie(mock_app):
    client = mock_app.test_client()
    response = client.post('/recommend', json={'movie_name': 'Movie1'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'recommendations' in data
    assert 'Movie2' in data['recommendations']

def test_recommend_invalid_movie(mock_app):
    client = mock_app.test_client()
    response = client.post('/recommend', json={'movie_name': 'Unknown Movie'})
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == 'Movie not found'
