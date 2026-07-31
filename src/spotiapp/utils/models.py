from dataclasses import dataclass


@dataclass
class SpotifySyncDelta:
    tracks_to_add: dict
    tracks_to_delete: list[tuple[str]]


@dataclass
class SpotifyIngestionPayload:
    tracks: dict
    albums: dict
    artists: dict
    track_artists: list[dict]
    track_tags: list[dict]
    tracks_to_add: dict
    tracks_to_delete: list[tuple[str]]
