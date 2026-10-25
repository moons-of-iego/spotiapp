from dataclasses import dataclass
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


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


class CircuitBreaker:
    def __init__(self):
        self.is_open = False
        self.reset_time = None

    def check_state(self):
        """Check if the pipeline is authorized to make API requests."""
        if self.is_open:
            if datetime.now() > self.reset_time:
                self.is_open = False
            else:
                remaining = (self.reset_time - datetime.now()).seconds
                raise ConnectionError(f"Circuit open. Try again in {remaining}s.")

    def trigger(self, retry_after_seconds):
        """Trigger the circuit breaker."""
        self.is_open = True
        self.reset_time = datetime.now() + timedelta(seconds=retry_after_seconds)
        logger.warning(
            f"Circuit breaker triggered. API called blocked for {retry_after_seconds}s."
        )
