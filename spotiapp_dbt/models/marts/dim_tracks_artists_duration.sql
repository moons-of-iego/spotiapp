SELECT
    lt.track_id,
    lt.track_name,
    ROUND(lt.duration_ms / 1000) AS duration_seconds,
    GROUP_CONCAT(a.artist_name SEPARATOR ', ') AS artist_names
FROM {{ ref('stg_tracks')}} lt
JOIN {{ ref('stg_track_artists')}} ta
ON lt.track_id = ta.track_id
JOIN {{ ref('stg_artists')}} a
ON a.artist_id = ta.artist_id
GROUP BY 
    lt.track_id,
    lt.track_name,
    lt.duration_ms
ORDER BY duration_seconds