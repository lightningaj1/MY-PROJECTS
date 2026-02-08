# app.py
from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    # Debug mode only in development (enable via environment variable)
    debug_mode = os.environ.get('DEBUG', 'False') == 'True'
    port = int(os.environ.get('PORT', 5000))
    
    app.run(debug=debug_mode, port=port, host='127.0.0.1')
