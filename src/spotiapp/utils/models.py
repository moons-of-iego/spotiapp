from dataclasses import dataclass


@dataclass
class SpotifyFormattedData:
    tracks: dict
    albums: dict
    artists: dict
    track_artists: list[dict]
    track_tags: list[dict]
