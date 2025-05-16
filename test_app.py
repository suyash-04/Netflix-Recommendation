from unittest.mock import patch
import pandas as pd

def test_home():
    with patch("app.routes.pd.read_csv") as mock_read_csv:
        mock_read_csv.return_value = pd.DataFrame()  # dummy data

        from run import app  # Import AFTER mocking

        response = app.test_client().get('/')

        assert response.status_code == 200
        assert response.data.decode('utf-8') == '<h1>Welcome to the Netflix Recommendation System</h1>'
