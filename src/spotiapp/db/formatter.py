from dataclasses import dataclass
import logging
from datetime import datetime
from spotiapp.utils.models import SpotifyFormattedData, SpotifyRawData

logger = logging.getLogger(__name__)


def _format_datetime(iso_date: str) -> str:
    """Convert a Spotify ISO 8601 timestamp to MySQL DATETIME format.

    Args:
        iso_date (str): Spotify raw timestamp (ex: '2026-05-08T21:02:36Z')

    Returns:
        str: A MySQL DATETIME formatted date: (ex: 2026-05-08 21:02:36 ')
    """
    mysql_timestamp = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
    return mysql_timestamp.strftime("%Y-%m-%d %H:%M:%S")


def _format_type_track(type_track: str) -> int:
    """Convert the type of track to a boolean information (0 or 1).

    Args:
        type_track (str): the type of track.

    Returns:
        int: 1 if type_track is "single", else 0.
    """
    return 1 if type_track == "single" else 0


def _format_track(track_id: str, track_data: dict) -> dict:
    """Extract track data."""
    return {
        "id": track_id,
        "name": track_data.get("name"),
        "album_id": track_data.get("album", {}).get("id"),
        "duration": track_data.get("duration_ms"),
        "url": track_data.get("external_urls", {}).get("spotify"),
        "date_added": _format_datetime(track_data.get("added_at")),
        "is_single": _format_type_track(track_data.get("type")),
    }


def _format_artist(artist_data: dict) -> dict:
    """Extract artist data."""
    return {
        "id": artist_data.get("id"),
        "name": artist_data.get("name"),
        "url": artist_data.get("external_urls", {}).get("spotify"),
    }


def _format_album(album_data: dict) -> dict:
    """Extract album data."""
    return {
        "id": album_data.get("id"),
        "name": album_data.get("name"),
        "type": album_data.get("album_type"),
        "url": album_data.get("external_urls", {}).get("spotify"),
    }


def _format_track_artists(artist_id: str, track_id: str) -> dict:
    """Extract the artist corresponding to the track."""
    return {"track_id": track_id, "artist_id": artist_id}


def _format_track_tag(tag: str, track_id: str) -> dict:
    """Extract the tag corresponding to the track."""
    return {"track_id": track_id, "tag": tag}


def format_raw_spotify_data(raw_data: SpotifyRawData) -> SpotifyFormattedData:
    """Format the data to be inserted on the database.

    Args:
        liked_tracks_dict (dict): the dictionnary containing the JSON data retrieved from Spotify API.
    """
    formatted_liked_tracks_dict = {}
    formatted_artists_dict = {}
    formatted_albums_dict = {}
    formatted_track_artist_list = []
    formatted_track_tag_list = []

    for track_id, track_data in raw_data.tracks_to_add.items():
        # -- 1. Format track data --
        if track_id not in formatted_liked_tracks_dict:
            formatted_liked_tracks_dict[track_id] = _format_track(track_id, track_data)

        # -- 2. Format artist(s) data and correspondance between track and artist --
        for artist_data in track_data.get("artists", {}):
            artist_id = artist_data.get("id")
            formatted_track_artist_list.append(
                _format_track_artists(artist_id, track_id)
            )
            if artist_id not in formatted_artists_dict:
                formatted_artists_dict[artist_id] = _format_artist(artist_data)

        # -- 3. Format album data --
        album_id = track_data.get("album", {}).get("id")
        if album_id not in formatted_albums_dict:
            formatted_albums_dict[album_id] = _format_album(track_data.get("album"))

        # -- 4. Format tag data --
        tags = track_data.get("tags", [])
        for tag in tags:
            formatted_track_tag_list.append(_format_track_tag(tag, track_id))

    logger.info(f"Successfully formatted {len(formatted_liked_tracks_dict)} tracks.")

    return SpotifyFormattedData(
        tracks=formatted_liked_tracks_dict,
        artists=formatted_artists_dict,
        albums=formatted_albums_dict,
        track_artists=formatted_track_artist_list,
        track_tags=formatted_track_tag_list,
    )
