import pandas as pd
import spotipy
import pylast
import spotiapp.config as config
from spotiapp.db.database_manager import DatabaseManager
from spotiapp.utils.models import SpotifySyncDelta
import logging
from spotipy import SpotifyOAuth
from spotiapp.utils.models import CircuitBreaker

logger = logging.getLogger(__name__)


class SpotifyDataGetter:
    def __init__(self, threshold: int = 20):
        self.sp = spotipy.Spotify(oauth_manager=SpotifyOAuth(scope=config.SCOPE))
        self.lastfm = pylast.LastFMNetwork(
            api_key=config.LASTFM_API_KEY, api_secret=config.LASTFM_API_SECRET
        )

        self.circuit_breaker = CircuitBreaker()

        self.liked_tracks_dict = {}
        self.playlists_dict = {}
        self.tracks_to_add = {}
        self.tracks_to_delete = list[tuple[str]]
        self.playlists_to_add = {}
        self.playlists_to_delete = list[tuple[str]]
        self.threshold: int = threshold
        self.user_id: str = None

    def execute_sp_call(self, sp_func, **kwargs):
        "Centralized wrapper to apply the circuit breaker and catch the ban duration to prevent spamming the Spotify API"
        self.circuit_breaker.check_state()

        try:
            return sp_func(**kwargs)
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 429:
                retry_after = (
                    3600  # default ban time if Spotify don't give it on the header
                )
                if hasattr(e, "headers") and e.headers and "Retry-After" in e.headers:
                    retry_after = int(e.headers["Retry-After"])

                self.circuit_breaker.trigger(retry_after_seconds=retry_after)

            raise e

    def get_user_id(self):
        if self.user_id is None:
            user_data = self.execute_sp_call(self.sp.current_user)
            self.user_id = user_data["account_id"]

    def _fetch_playlists(self):
        offset = 0
        while True:
            try:
                response = self.execute_sp_call(
                    self.sp.current_user_playlists, limit=50, offset=offset
                )
                items = response["items"]
                if len(items) == 0:
                    break
                for item in items:
                    if item["id"] not in self.playlists_dict:
                        playlist_id = item.get("id")
                        playlist_name = item.get("name")
                        playlist_tracks = self._fetch_playlist_tracks(
                            playlist_id, playlist_name
                        )
                        self.playlists_dict[item["id"]] = {
                            "name": item["name"],
                            "url": item["external_urls"]["spotify"],
                            "tracks": playlist_tracks,
                        }
                    else:
                        pass
                offset += len(items)
            except Exception as e:
                logger.error(f"Erreur en récupérant les données de playlist: {e}")
                raise e

    def _fetch_playlist_tracks(self, playlist_id: str, playlist_name: str):
        """Fetch all the tracks contained on a specific playlist.

        :parameter str playlist_id: the unique ID of the playlist.
        :return: the list of the playlist tracks' IDs.
        """
        offset = 0
        track_ids = []
        logger.info(f"Tentative d'accès à la playlist {playlist_name}")

        while True:
            try:
                response = self.execute_sp_call(
                    self.sp.playlist_items,
                    playlist_id=playlist_id,
                    limit=100,
                    offset=offset,
                    market="FR",
                )
                items = response["items"]
                if len(items) == 0:
                    break
                for item in items:
                    id = item["item"]["id"]
                    if id not in track_ids:
                        track_ids.append(id)
                offset += len(items)
            except spotipy.exceptions.SpotifyException as e:
                if e.http_status == 403:  # accès à la playlist interdit
                    logger.warning(f"Accès à la playlist {playlist_name} interdit: {e}")
                    break
                else:
                    raise e
            except Exception as e:
                break
        logger.info(f"Accès à la playlist {playlist_name} réussie")
        return track_ids

    def get_spotify_data(self, force_reload) -> SpotifySyncDelta:
        self._fetch_saved_tracks()
        self._fetch_playlists()
        self._get_sync_delta_tracks(force_reload)
        self._link_tags_data()

        return SpotifySyncDelta(
            tracks_to_add=self.tracks_to_add, tracks_to_delete=self.tracks_to_delete
        )

    def _fetch_saved_tracks(self):
        """
        Fetch the list of the liked tracks on the Spotify account.
        Uses the official Spotify API to get the data."""
        offset = 0
        while True:
            try:
                response = self.execute_sp_call(
                    self.sp.current_user_saved_tracks,
                    limit=50,
                    offset=offset,
                    market="FR",
                )
                items = response["items"]
                if len(items) == 0:
                    break
                for item in items:
                    if item["track"]["id"] not in self.liked_tracks_dict:
                        item["track"]["added_at"] = item["added_at"]
                        self.liked_tracks_dict[item["track"]["id"]] = item["track"]
                    else:
                        pass
                offset += len(items)
            except Exception as e:
                logger.error(e)
                raise e

    def _get_sync_delta_tracks(self, force_reload: bool):
        """Keep only the tracks not only inserted on the database."""
        query = "SELECT id FROM liked_tracks;"
        liked_tracks_on_bdd = DatabaseManager.execute_transaction(
            query=query, verbose=True
        )
        liked_tracks_on_spotify = pd.DataFrame(
            self.liked_tracks_dict.keys(), columns=["id"]
        )
        # tracks liked on Spotify, but not inserted on DB yet
        if not force_reload:
            id_tracks_to_add = liked_tracks_on_spotify[
                ~liked_tracks_on_spotify["id"].isin(liked_tracks_on_bdd["id"])
            ]
            self.tracks_to_add = {
                id: self.liked_tracks_dict[id] for id in id_tracks_to_add["id"]
            }
        else:
            logger.info("FORCE RELOAD ENABLED")
            self.tracks_to_add = self.liked_tracks_dict

        # tracks inserted on DB but unliked on Spotify since
        id_tracks_to_delete = liked_tracks_on_bdd[
            ~liked_tracks_on_bdd["id"].isin(liked_tracks_on_spotify["id"])
        ]
        self.tracks_to_delete = list(
            id_tracks_to_delete.itertuples(index=False, name=None)
        )

    def _get_sync_delta_playlists(self, force_reload: bool):
        query = "SELECT id FROM playlists;"
        playlists_on_db = DatabaseManager.execute_transaction(query=query, verbose=True)

        playlists_on_spotify = ...

    def _link_tags_data(self):
        """
        Get tags data for a list of liked tracks.
        """
        count = 0
        count_liked_tracks = len(self.tracks_to_add)
        if count_liked_tracks == 0:
            return
        logger.info(f"{count_liked_tracks} new tracks. Getting tags ...")
        for track, track_data in self.tracks_to_add.items():
            artists_names = []
            top_tags_list = []
            track_name = track_data["name"]
            artists_names = [artist["name"] for artist in track_data["artists"]]
            try:
                # search for the lastfm track with all featured artists
                for artist in artists_names:
                    track_obj = self.lastfm.get_track(artist=artist, title=track_name)
                    if track_obj:  # take the first lastfm track object got
                        break

                top_tags = track_obj.get_top_tags()
                # if a tag is found
                if len(top_tags) != 0:
                    for tag in top_tags:
                        if int(tag.weight) >= self.threshold:
                            top_tags_list.append(tag.item.get_name())
                else:  # if no tags exists for the track, the tag is fetched from the artist
                    top_tags_list = self.__get_artist_top_tags(track_obj)

                self.tracks_to_add[track]["tags"] = top_tags_list
                logger.info(
                    f"Got tags for {track_data['name']} ({count} / {count_liked_tracks})"
                )
                count += 1

            except Exception as e:
                logger.error(f"track {track}: error {e}")

        logger.info(f"Collected and enriched {len(self.tracks_to_add)} tracks.")

    def __get_artist_top_tags(self, track_obj: pylast.Track) -> list[str]:
        """
        Get the top tags of the artist. It is less precise than the top tags of the track itself, but a good proxy for the track's tag.

        :param pylast.Track track_obj: a Pylast Track instance.
        :return list[str] tags_list: the list of the artist's tags with a weight higher than instance threshold.
        """
        try:
            tags = track_obj.get_artist().get_top_tags()
            tags_list = [
                tag.item.get_name() for tag in tags if int(tag.weight) > self.threshold
            ]
            return tags_list
        except Exception as e:
            logger.error(f"error: {e}")
