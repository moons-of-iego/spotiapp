import pandas as pd
import spotipy
import pylast
import spotiapp.config as config
from spotiapp.db.database_manager import DatabaseManager
from spotiapp.utils.models import SpotifyRawData
import logging
from spotipy import SpotifyOAuth

logger = logging.getLogger(__name__)


class SpotifyDataGetter:
    def __init__(self, threshold: int = 20):
        scope = "user-library-read"
        self.sp = spotipy.Spotify(oauth_manager=SpotifyOAuth(scope=scope))
        self.lastfm = pylast.LastFMNetwork(
            api_key=config.LASTFM_API_KEY, api_secret=config.LASTFM_API_SECRET
        )

        self.liked_tracks_dict = {}
        self.duplicates = {}
        self.tracks_to_add = {}
        self.tracks_to_delete = list[tuple[str]]
        self.threshold = threshold

    def get_liked_tracks_data(self) -> SpotifyRawData:
        self._fetch_saved_tracks()
        self._get_tracks_not_inserted_yet()
        self._link_tags_data()
        print(f"Collected and enriched {len(self.tracks_to_add)} tracks.")

        return SpotifyRawData(
            tracks_to_add=self.tracks_to_add, tracks_to_delete=self.tracks_to_delete
        )

    def _fetch_saved_tracks(self):
        """
        Fetch the list of the liked tracks on the Spotify account.
        Uses the official Spotify API to get the data."""
        offset = 0
        while True:
            try:
                response = self.sp.current_user_saved_tracks(
                    limit=50, offset=offset, market="FR"
                )
                items = response["items"]
                if len(items) == 0:
                    break
                for item in items:
                    if item["track"]["id"] not in self.liked_tracks_dict:
                        item["track"]["added_at"] = item["added_at"]
                        self.liked_tracks_dict[item["track"]["id"]] = item["track"]
                    else:
                        self.duplicates.append(item)
                offset += len(items)
            except Exception as e:
                print(e)

    def _get_tracks_not_inserted_yet(self):
        """Keep only the tracks not only inserted on the database."""
        query = "SELECT id FROM liked_tracks;"
        liked_tracks_on_bdd = DatabaseManager.execute_transaction(
            query=query, verbose=True
        )
        liked_tracks_on_spotify = pd.DataFrame(
            self.liked_tracks_dict.keys(), columns=["id"]
        )
        # tracks liked on Spotify, but not inserted on DB yet
        id_tracks_to_add = liked_tracks_on_spotify[
            ~liked_tracks_on_spotify["id"].isin(liked_tracks_on_bdd["id"])
        ]
        self.tracks_to_add = {
            id: self.liked_tracks_dict[id] for id in id_tracks_to_add["id"]
        }

        # tracks inserted on DB but unliked on Spotify since
        id_tracks_to_delete = liked_tracks_on_bdd[
            ~liked_tracks_on_bdd["id"].isin(liked_tracks_on_spotify["id"])
        ]
        self.tracks_to_delete = list(
            id_tracks_to_delete.itertuples(index=False, name=None)
        )

    def _link_tags_data(self):
        """
        Get tags data for a list of liked tracks.
        """
        count = 0
        count_liked_tracks = len(self.tracks_to_add)
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
