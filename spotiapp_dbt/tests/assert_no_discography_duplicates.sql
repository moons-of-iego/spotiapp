-- Look for the duplicated tracks with different id (= if an artist publishes many times the same song)
SELECT 
    track_name, 
    artist_names, 
    COUNT(*)
FROM {{ ref ('dim_tracks_enriched')}}
GROUP BY 
    track_name, 
    artist_names
HAVING COUNT(*) > 1