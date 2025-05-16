from unittest.mock import patch
import pandas as pd
import pytest

# Patch pandas.read_csv in the app.routes module
@patch("app.routes.pd.read_csv")
def test_home(mock_read_csv):
    # Mock return value for the CSV
    mock_read_csv.return_value = pd.DataFrame()  # Empty dummy DataFrame

    from run import app  # Import after mocking to avoid triggering real read_csv

    response = app.test_client().get('/')

    assert response.status_code == 200
    assert response.data.decode('utf-8') == '<h1>Welcome to the Netflix Recommendation System</h1>'
