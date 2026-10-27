INSERT_INTO_ALBUMS = """
    INSERT INTO albums (id, name, url)
    VALUES (%(id)s, %(name)s, %(url)s)
    ON DUPLICATE KEY UPDATE 
        name = VALUES(name),
        url = VALUES(url);     
"""

INSERT_INTO_ARTISTS = """
    INSERT INTO artists (id, name, url)
    VALUES (%(id)s, %(name)s, %(url)s)
    ON DUPLICATE KEY UPDATE 
        name = VALUES(name),
        url = VALUES(url);
"""

INSERT_INTO_TRACKS = """
    INSERT INTO tracks (id, name, album_id, duration, url, is_single)
    VALUES (%(id)s, %(name)s, %(album_id)s, %(duration)s, %(url)s, %(is_single)s)
    ON DUPLICATE KEY UPDATE 
        name = VALUES(name),
        album_id = VALUES(album_id),
        duration = VALUES(duration),
        url = VALUES(url),
        is_single = VALUES(is_single);
"""

INSERT_INTO_LIKED_TRACKS = """
    INSERT INTO liked_tracks (track_id, date_added)
    VALUES (%(track_id)s, %(date_added)s)
    ON DUPLICATE KEY UPDATE
        date_added = VALUES(date_added);
"""

INSERT_INTO_TRACK_ARTIST = """
    INSERT IGNORE INTO track_artists (track_id, artist_id)
    VALUES (%(track_id)s, %(artist_id)s);
"""

INSERT_INTO_TRACK_TAG = """
    INSERT IGNORE INTO track_tags (track_id, tag)
    VALUES (%(track_id)s, %(tag)s);
"""

DELETE_FROM_TRACKS = """
    DELETE FROM liked_tracks WHERE track_id = %s;
"""
