import logging
from spotiapp.db.database_manager import DatabaseManager
from spotiapp.db.extractor import SpotifyDataGetter
from spotiapp.db.formatter import format_raw_spotify_data
from spotiapp.db.loader import update_database
from pathlib import Path
import spotiapp.config as config

logger = logging.getLogger(__name__)


def run(force_reload: bool = False):
    DatabaseManager.initialize(pool_size=5)
    spotify_data_getter = SpotifyDataGetter()
    spotify_sync_delta = spotify_data_getter.get_liked_tracks_data(force_reload)

    spotify_ingestion_payload = format_raw_spotify_data(spotify_sync_delta)
    update_database(spotify_ingestion_payload)


def update_database_scheme(path: Path):
    DatabaseManager.update_database_scheme(path)
