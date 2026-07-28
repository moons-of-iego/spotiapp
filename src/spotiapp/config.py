from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

CODE_ROOT = Path(__file__).parent.parent.parent
SQL_DIR = CODE_ROOT / "sql"


def _load_sql_query(path: Path) -> str:
    with path.open("r", encoding="utf-8") as f:
        return f.read()


# LASTFM config
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
LASTFM_API_SECRET = os.getenv("LASTFM_SHARED_SECRET")

# database config
NAME_DB = os.getenv("DATABASE_NAME")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
USER_LOGIN = os.getenv("ROOT_USER")
USER_PASSWORD = os.getenv("ROOT_USER_PASSWORD")

# static queries
INIT_DB = _load_sql_query(SQL_DIR / "schema.sql")
