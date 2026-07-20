import spotipy
import pylast
import config
import logging
from spotipy import SpotifyOAuth

logger = logging.GetLogger(__name__)


class SpotifyDataGetter:
    def __init__(self, threshold: int = 20):
        scope = "user-library-read"
        self.sp = spotipy.Spotify(oauth_manager=SpotifyOAuth(scope=scope))
        self.lastfm = pylast.LastFMNetwork(
            api_key=config.LASTFM_API_KEY, api_secret=config.LASTFM_API_SECRET
        )

        self.liked_tracks_dict = {}
        self.duplicates = {}
        self.threshold = threshold

    def get_liked_tracks_data(self) -> dict:
        self._get_saved_tracks()
        self._link_tags_data()
        print(f"Collected and enriched {len(self.liked_tracks_dict)} tracks.")

        return self.liked_tracks_dict

    def _get_saved_tracks(self):
        """
        Get the list of the liked tracks on the Spotify account.
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

    def _link_tags_data(self):
        """
        Get tags data for a list of liked tracks.
        """
        count = 0
        count_liked_tracks = len(self.liked_tracks_dict)
        for track, track_data in self.liked_tracks_dict.items():
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

                self.liked_tracks_dict[track]["tags"] = top_tags_list
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
