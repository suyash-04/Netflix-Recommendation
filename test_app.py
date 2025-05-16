from run import app

def test_home():
    response = app.test_client().get('/')
    
    assert response.status_code == 200 # type: ignore
    assert response.data.decode('utf-8') == '<h1>Welcome to the Netflix Recommendation System</h1>' # type: ignore