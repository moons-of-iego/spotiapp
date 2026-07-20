from src.spotiapp.db.pool_manager import DatabaseManager
from src.spotiapp.utils.enums import Tables
from src.spotiapp.utils.models import SpotifyFormattedData
import src.spotiapp.db.queries as queries
import logging

logger = logging.getLogger(__name__)


def load_data_in_database(data: SpotifyFormattedData):
    _load_table_data_from_dict(
        data.albums, query=queries.INSERT_INTO_ALBUMS, table=Tables.ALBUMS
    )
    _load_table_data_from_dict(
        data.artists, query=queries.INSERT_INTO_ARTISTS, table=Tables.ARTISTS
    )
    _load_table_data_from_dict(
        data.tracks, query=queries.INSERT_INTO_LIKED_TRACKS, table=Tables.TRACKS
    )
    _load_table_data_from_list(
        data.track_artists,
        query=queries.INSERT_INTO_TRACK_ARTIST,
        table=Tables.TRACK_ARTISTS,
    )
    _load_table_data_from_list(
        data.track_tags, query=queries.INSERT_INTO_TRACK_TAG, table=Tables.TRACK_TAGS
    )


def _load_table_data_from_dict(data: dict, query: str, table: Tables):
    """Load the data for a particular table."""
    try:
        DatabaseManager.executemany_transactions(
            query=query, seq_of_params=list(data.values())
        )
        logger.info(f"Successfully inserted {len(data)} records into {table.value}")
    except Exception as e:
        logger.error(f"Failed to insert on table {table}: {e}")


def _load_table_data_from_list(data: list, query: str, table: Tables):
    try:
        DatabaseManager.executemany_transactions(query=query, seq_of_params=data)
        logger.info(f"Successfully inserted {len(data)} records into {table.value}")
    except Exception as e:
        logger.error(f"Failed to insert on table {table}: {e}")
