# app.py
from app import create_app

app = create_app()

# Only run locally (development)
if __name__ == "__main__":
    import os
    debug_mode = os.environ.get('DEBUG', 'False') == 'True'
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug_mode, host="0.0.0.0", port=port)

