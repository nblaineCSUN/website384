# fruitapp.wsgi.py (shared across machines)
import os, sys

# Make everything relative to this file's folder, no hardcoded machine paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Optional: if your app uses a relative SQLite path, ensure cwd is the project root
os.chdir(BASE_DIR)

# Import the Flask app object from app.py
from app import app as application
