import logging
from spotiapp.db.database_manager import DatabaseManager
from spotiapp.db.extractor import SpotifyDataGetter
from spotiapp.db.formatter import format_raw_spotify_data
from spotiapp.db.loader import load_data_in_database
import spotiapp.config as config

logger = logging.getLogger(__name__)


def run():
    DatabaseManager.initialize(pool_size=5)
    spotify_data_getter = SpotifyDataGetter()
    liked_tracks_dict = spotify_data_getter.get_liked_tracks_data()

    spotify_formatted_data = format_raw_spotify_data(liked_tracks_dict)
    load_data_in_database(spotify_formatted_data)
