"""
Study Buddy - Flask Application Entry Point
This is the main Flask app file that the Dockerfile will run
"""

import os

# Import the main application from main.py
from main import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print("🚀 Starting Study Buddy via Docker...")
    print(f"🌐 Server running on 0.0.0.0:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
