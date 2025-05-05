from app import app
import webbrowser
import os
import time

def print_banner():
    print("\n" + "=" * 80)
    print(" 🎬 NETFLIX RECOMMENDATION SYSTEM 🎬 ".center(80))
    print("=" * 80)
    print("\n📋 Features:".ljust(80))
    print("  • Movie recommendations based on content similarity")
    print("  • Detailed movie information")
    print("  • Sentiment analysis of reviews")
    print("\n🔗 Access the application at: http://localhost:5000")
    print("\n📸 To add screenshots for documentation:")
    print("  1. Navigate to each main page of the application")
    print("  2. Take screenshots and save them in the 'screenshots' folder as:")
    print("     - homepage.png")
    print("     - recommendations.png")
    print("     - movie_details.png")
    print("     - sentiment.png")
    print("=" * 80 + "\n")
    
if __name__ == '__main__':
    # Create screenshots directory if it doesn't exist
    screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screenshots')
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
        
    print_banner()
    
    # Open browser automatically after a short delay
    url = "http://localhost:5000"
    webbrowser.open_new(url)
    
    # Run the Flask application
    app.run(debug=True, host='0.0.0.0', port=5000) 