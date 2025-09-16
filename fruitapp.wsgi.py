# /mnt/c/Users/nblai/Downloads/PROJECTS/citFallSem/website/fruitapp.wsgi.py
import sys, os

# Add the project directory to the path
PROJECT_DIR = r"/mnt/c/Users/nblai/Downloads/PROJECTS/citFallSem/website"
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# If your Flask app factory lives in app.py and exposes 'app'
from app import app as application  # <-- 'application' is what mod_wsgi looks for

# Optional: set a safer working dir for things like relative DB paths
os.chdir(PROJECT_DIR)
