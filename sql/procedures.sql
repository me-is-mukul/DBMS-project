DROP PROCEDURE IF EXISTS GetUserById;
DROP PROCEDURE IF EXISTS GetPlaylistsByUser;
DROP PROCEDURE IF EXISTS CreatePlaylist;
DROP PROCEDURE IF EXISTS AddSongToPlaylist;
DROP PROCEDURE IF EXISTS DeletePlaylist;
DROP PROCEDURE IF EXISTS GetFollowedArtists;
DROP PROCEDURE IF EXISTS GetAllArtists;
DROP PROCEDURE IF EXISTS FollowArtist;
DROP PROCEDURE IF EXISTS UnfollowArtist;
DROP PROCEDURE IF EXISTS GetFollowedArtistIds;

DROP PROCEDURE IF EXISTS Admin_TopArtists;
DROP PROCEDURE IF EXISTS Admin_UsersMostPlaylists;
DROP PROCEDURE IF EXISTS Admin_ViewTable;
DROP PROCEDURE IF EXISTS Admin_TopGenres;
DROP PROCEDURE IF EXISTS Admin_UsersWithMostFollows;
DROP PROCEDURE IF EXISTS Admin_AvgPlaylists;

DELIMITER $$

-- ============================================================
-- Get User by ID
-- ============================================================
CREATE PROCEDURE GetUserById(IN uid VARCHAR(64))
BEGIN
    SELECT *
    FROM `User`
    WHERE user_id = uid;
END $$


-- ============================================================
-- Get playlists for a user
-- ============================================================
CREATE PROCEDURE GetPlaylistsByUser(IN uid VARCHAR(64))
BEGIN
    SELECT playlist_id, playlist_name, created_date
    FROM Playlist
    WHERE user_id = uid
    ORDER BY created_date DESC;
END $$


-- ============================================================
-- Create playlist
-- ============================================================
CREATE PROCEDURE CreatePlaylist(
    IN uid VARCHAR(64),
    IN pid VARCHAR(64),
    IN pname VARCHAR(255),
    IN cdate DATE
)
BEGIN
    INSERT INTO Playlist(playlist_id, playlist_name, created_date, user_id)
    VALUES(pid, pname, cdate, uid);
END $$


-- ============================================================
-- Add song to playlist
-- ============================================================
CREATE PROCEDURE AddSongToPlaylist(
    IN pid VARCHAR(64),
    IN sid VARCHAR(64)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Playlist WHERE playlist_id = pid) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid playlist';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Song WHERE song_id = sid) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid song';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM SongsInPlaylist
        WHERE playlist_id = pid AND song_id = sid
    ) THEN
        INSERT INTO SongsInPlaylist(playlist_id, song_id)
        VALUES(pid, sid);
    END IF;
END $$


-- ============================================================
-- Delete playlist (only owner can delete)
-- ============================================================
CREATE PROCEDURE DeletePlaylist(IN pid VARCHAR(64), IN uid VARCHAR(64))
BEGIN
    DELETE FROM SongsInPlaylist WHERE playlist_id = pid;
    DELETE FROM Playlist WHERE playlist_id = pid AND user_id = uid;
END $$


-- ============================================================
-- Get followed artists
-- ============================================================
CREATE PROCEDURE GetFollowedArtists(IN uid VARCHAR(64))
BEGIN
    SELECT a.artist_id, a.first_name, a.last_name
    FROM Artist a
    JOIN Follows f ON a.artist_id = f.artist_id
    WHERE f.user_id = uid
    ORDER BY a.last_name, a.first_name;
END $$


-- ============================================================
-- Get only artist IDs user follows
-- ============================================================
CREATE PROCEDURE GetFollowedArtistIds(IN uid VARCHAR(64))
BEGIN
    SELECT artist_id
    FROM Follows
    WHERE user_id = uid;
END $$


-- ============================================================
-- Get all artists
-- ============================================================
CREATE PROCEDURE GetAllArtists()
BEGIN
    SELECT artist_id, first_name, last_name
    FROM Artist
    ORDER BY last_name, first_name;
END $$


-- ============================================================
-- Follow artist
-- ============================================================
CREATE PROCEDURE FollowArtist(IN uid VARCHAR(64), IN aid VARCHAR(64))
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Artist WHERE artist_id = aid) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid artist';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM Follows WHERE user_id = uid AND artist_id = aid
    ) THEN
        INSERT INTO Follows(user_id, artist_id)
        VALUES(uid, aid);
    END IF;
END $$


-- ============================================================
-- Unfollow artist
-- ============================================================
CREATE PROCEDURE UnfollowArtist(IN uid VARCHAR(64), IN aid VARCHAR(64))
BEGIN
    DELETE FROM Follows
    WHERE user_id = uid AND artist_id = aid;
END $$


-- ============================================================
-- Admin: Top Artists by Followers
-- ============================================================
CREATE PROCEDURE Admin_TopArtists()
BEGIN
    SELECT a.artist_id,
           CONCAT(IFNULL(a.first_name,''),' ',IFNULL(a.last_name,'')) AS artist_name,
           COUNT(f.user_id) AS follower_count
    FROM Artist a
    LEFT JOIN Follows f ON a.artist_id = f.artist_id
    GROUP BY a.artist_id
    ORDER BY follower_count DESC, artist_name
    LIMIT 100;
END $$


-- ============================================================
-- Admin: Users with Most Playlists
-- ============================================================
CREATE PROCEDURE Admin_UsersMostPlaylists()
BEGIN
    SELECT u.user_id,
           CONCAT(u.first_name,' ',IFNULL(u.second_name,'')) AS user_name,
           COUNT(p.playlist_id) AS playlist_count
    FROM `User` u
    LEFT JOIN Playlist p ON u.user_id = p.user_id
    GROUP BY u.user_id
    ORDER BY playlist_count DESC, user_name
    LIMIT 100;
END $$


-- ============================================================
-- Admin: View any table
-- ============================================================
CREATE PROCEDURE Admin_ViewTable(IN tname VARCHAR(64))
BEGIN
    SET @s = CONCAT('SELECT * FROM `', tname, '` LIMIT 1000');
    PREPARE stmt FROM @s;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END $$


-- ============================================================
-- Admin: Top Genres
-- ============================================================
CREATE PROCEDURE Admin_TopGenres()
BEGIN
    SELECT genre, COUNT(*) AS song_count
    FROM Song
    WHERE genre IS NOT NULL AND genre <> ''
    GROUP BY genre
    ORDER BY song_count DESC
    LIMIT 10;
END $$


-- ============================================================
-- Admin: Users with most follows
-- ============================================================
CREATE PROCEDURE Admin_UsersWithMostFollows()
BEGIN
    SELECT u.user_id,
           CONCAT(u.first_name,' ',IFNULL(u.second_name,'')) AS name,
           COUNT(f.artist_id) AS follows
    FROM `User` u
    LEFT JOIN Follows f ON u.user_id = f.user_id
    GROUP BY u.user_id
    ORDER BY follows DESC
    LIMIT 20;
END $$


-- ============================================================
-- Admin: Average playlists per user
-- ============================================================
CREATE PROCEDURE Admin_AvgPlaylists()
BEGIN
    SELECT ROUND(AVG(cnt), 2) AS avg_playlists_per_user
    FROM (
        SELECT COUNT(*) AS cnt
        FROM Playlist
        GROUP BY user_id
    ) AS t;
END $$

DELIMITER ;
