from spotiapp.db.database_manager import DatabaseManager
from spotiapp.utils.enums import Tables
from spotiapp.utils.models import SpotifyIngestionPayload, SpotifySyncDelta
import spotiapp.db.queries as queries
import logging

logger = logging.getLogger(__name__)


def update_database(ingestion_payload: SpotifyIngestionPayload):
    _load_data_in_database(data=ingestion_payload)
    _delete_unliked_tracks(data=ingestion_payload)


def _load_data_in_database(data: SpotifyIngestionPayload):
    if len(data.tracks_to_add) == 0:
        logger.info("No new tracks to add.")
        if len(data.liked_tracks_to_add) == 0:
            logger.info("No new liked tracks to add.")
            return
    _load_table_data_from_dict(
        data.albums, query=queries.INSERT_INTO_ALBUMS, table=Tables.ALBUMS
    )
    _load_table_data_from_dict(
        data.artists, query=queries.INSERT_INTO_ARTISTS, table=Tables.ARTISTS
    )
    _load_table_data_from_dict(
        data.tracks, query=queries.INSERT_INTO_TRACKS, table=Tables.TRACKS
    )
    _load_table_data_from_list(
        data.track_artists,
        query=queries.INSERT_INTO_TRACK_ARTIST,
        table=Tables.TRACK_ARTISTS,
    )
    _load_table_data_from_list(
        data.track_tags, query=queries.INSERT_INTO_TRACK_TAG, table=Tables.TRACK_TAGS
    )
    _load_table_data_from_dict(
        data.liked_tracks,
        query=queries.INSERT_INTO_LIKED_TRACKS,
        table=Tables.LIKED_TRACKS,
    )


def _load_table_data_from_dict(data: dict, query: str, table: Tables):
    """Load the data for a particular table."""
    if len(data) == 0:
        return
    try:
        DatabaseManager.executemany_transactions(
            query=query, seq_of_params=list(data.values())
        )
        logger.info(f"Successfully inserted {len(data)} records into {table.value}")
    except Exception as e:
        logger.error(f"Failed to insert on table {table}: {e}")


def _load_table_data_from_list(data: list, query: str, table: Tables):
    if len(data) == 0:
        return
    try:
        DatabaseManager.executemany_transactions(query=query, seq_of_params=data)
        logger.info(f"Successfully inserted {len(data)} records into {table.value}")
    except Exception as e:
        logger.error(f"Failed to insert on table {table}: {e}")


def _delete_unliked_tracks(data: SpotifySyncDelta):
    if len(data.liked_tracks_to_delete) == 0:
        logger.info("No liked tracks to delete.")
        return
    try:
        DatabaseManager.executemany_transactions(
            query=queries.DELETE_FROM_TRACKS, seq_of_params=data.liked_tracks_to_delete
        )
        logger.info(
            f"Successfully deleted {len(data.liked_tracks_to_delete)} tracks from liked tracks."
        )
    except Exception as e:
        logger.error(f"Failed to delete from {Tables.LIKED_TRACKS.value}: {e}")
