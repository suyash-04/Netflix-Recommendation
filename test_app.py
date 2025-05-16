import pytest
from unittest.mock import patch, MagicMock
import pandas as pd

# Create a simple mock for movie_data
mock_csv_data = pd.DataFrame({
    'title': ['The Shawshank Redemption', 'The Godfather', 'Pulp Fiction'],
    'genres': ['Drama', 'Crime', 'Crime'],
    'director': ['Frank Darabont', 'Francis Ford Coppola', 'Quentin Tarantino'],
    'actors': ['Tim Robbins, Morgan Freeman', 'Marlon Brando, Al Pacino', 'John Travolta, Samuel L. Jackson'],
    'index': [0, 1, 2]
})

# Patch pandas.read_csv and pickle.load before importing app
@pytest.fixture(autouse=True)
def mock_dependencies(monkeypatch):
    # Mock pandas.read_csv
    def mock_read_csv(*args, **kwargs):
        return mock_csv_data
    
    monkeypatch.setattr(pd, 'read_csv', mock_read_csv)
    
    # Mock pickle.load if needed
    def mock_pickle_load(*args, **kwargs):
        return MagicMock()
    
    import pickle
    monkeypatch.setattr(pickle, 'load', mock_pickle_load)

# Now import app after mocking
from run import app

def test_home():
    response = app.test_client().get('/')
    
    assert response.status_code == 200 # type: ignore
    assert response.data.decode('utf-8') == '<h1>Welcome to the Netflix Recommendation System</h1>' # type: ignore