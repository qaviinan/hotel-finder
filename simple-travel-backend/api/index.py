import os
import sys

# Ensure sibling modules (e.g. app.py, chat_config.py) are importable on Vercel.
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import app
