USE spotiapp;

CREATE TABLE IF NOT EXISTS albums (
    id VARCHAR(50) PRIMARY KEY, 
    name VARCHAR(512),
    type VARCHAR(50),
    url VARCHAR(250)
);

CREATE TABLE IF NOT EXISTS artists (
    id VARCHAR(50) PRIMARY KEY, 
    name VARCHAR(100),
    url VARCHAR(250)
);

CREATE TABLE IF NOT EXISTS liked_tracks (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(512),
    album_id VARCHAR(50), 
    duration INTEGER,
    url VARCHAR(250), 
    date_added DATETIME,
    is_single BOOL,

    FOREIGN KEY (album_id) REFERENCES albums(id)
);

CREATE TABLE IF NOT EXISTS track_tags (
    track_id VARCHAR(50) NOT NULL,
    tag VARCHAR(100) NOT NULL

    PRIMARY KEY (track_id, tag),
    FOREIGN KEY (track_id) REFERENCES liked_tracks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS track_artists (
    track_id VARCHAR(50) NOT NULL,
    artist_id VARCHAR(50) NOT NULL,

    PRIMARY KEY (track_id, artist_id),
    FOREIGN KEY (track_id) REFERENCES liked_tracks(id) ON DELETE CASCADE,
    FOREIGN KEY (artist_id) REFERENCES artists(id) ON DELETE CASCADE
);