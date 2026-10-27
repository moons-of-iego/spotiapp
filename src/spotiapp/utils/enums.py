from enum import StrEnum


class Tables(StrEnum):
    TRACKS = "tracks"
    LIKED_TRACKS = "liked_tracks"
    ALBUMS = "albums"
    ARTISTS = "artists"
    TRACK_ARTISTS = "track_artists"
    TRACK_TAGS = "track_tags"
