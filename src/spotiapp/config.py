from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# LASTFM config
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
LASTFM_API_SECRET = os.getenv("LASTFM_SHARED_SECRET")

# database config
NAME_DB = os.getenv("DATABASE_NAME")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
USER_LOGIN = os.getenv("ROOT_USER")
USER_PASSWORD = os.getenv("ROOT_USER_PASSWORD")
