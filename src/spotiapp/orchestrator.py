import logging
from src.spotiapp.db.pool_manager import DatabaseManager
from src.spotiapp.db.extractor import SpotifyDataGetter
from src.spotiapp.db.formatter import format_raw_spotify_data
from src.spotiapp.db.loader import load_data_in_database
import src.spotiapp.config as config

logger = logging.getLogger(__name__)


def run():
    DatabaseManager.initialize(pool_size=5)
    # DatabaseManager.executescript_transaction(config.INIT_DB)
    spotify_data_getter = SpotifyDataGetter()
    liked_tracks_dict = spotify_data_getter.get_liked_tracks_data()

    spotify_formatted_data = format_raw_spotify_data(liked_tracks_dict)
    load_data_in_database(spotify_formatted_data)
