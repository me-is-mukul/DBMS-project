DROP FUNCTION IF EXISTS random_suffix;
DROP FUNCTION IF EXISTS gen_user_id;
DROP FUNCTION IF EXISTS gen_artist_id;
DROP FUNCTION IF EXISTS gen_song_id;
DROP FUNCTION IF EXISTS gen_playlist_id;

DELIMITER $$

-- Generates random alphanumeric suffix of given length
CREATE FUNCTION random_suffix(n INT)
RETURNS VARCHAR(32)
DETERMINISTIC
BEGIN
    DECLARE chars VARCHAR(64) DEFAULT 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    DECLARE output VARCHAR(64) DEFAULT '';
    DECLARE i INT DEFAULT 1;

    WHILE i <= n DO
        SET output = CONCAT(
            output,
            SUBSTRING(chars, FLOOR(1 + (RAND() * LENGTH(chars))), 1)
        );
        SET i = i + 1;
    END WHILE;

    RETURN output;
END $$


-- Generate USER ID
CREATE FUNCTION gen_user_id()
RETURNS VARCHAR(64)
DETERMINISTIC
BEGIN
    DECLARE candidate VARCHAR(64);
    DECLARE cnt INT DEFAULT 1;
    DECLARE attempts INT DEFAULT 0;

    WHILE cnt > 0 AND attempts < 50 DO
        SET candidate = CONCAT('USER-', random_suffix(4));
        SELECT COUNT(*) INTO cnt FROM `User` WHERE user_id = candidate;
        SET attempts = attempts + 1;
    END WHILE;

    IF cnt = 0 THEN
        RETURN candidate;
    END IF;

    RETURN CONCAT('USER-', UNIX_TIMESTAMP());
END $$


-- Generate ARTIST ID
CREATE FUNCTION gen_artist_id()
RETURNS VARCHAR(64)
DETERMINISTIC
BEGIN
    DECLARE candidate VARCHAR(64);
    DECLARE cnt INT DEFAULT 1;
    DECLARE attempts INT DEFAULT 0;

    WHILE cnt > 0 AND attempts < 50 DO
        SET candidate = CONCAT('ARTIST-', random_suffix(4));
        SELECT COUNT(*) INTO cnt FROM Artist WHERE artist_id = candidate;
        SET attempts = attempts + 1;
    END WHILE;

    IF cnt = 0 THEN
        RETURN candidate;
    END IF;

    RETURN CONCAT('ARTIST-', UNIX_TIMESTAMP());
END $$


-- Generate SONG ID
CREATE FUNCTION gen_song_id()
RETURNS VARCHAR(64)
DETERMINISTIC
BEGIN
    DECLARE candidate VARCHAR(64);
    DECLARE cnt INT DEFAULT 1;
    DECLARE attempts INT DEFAULT 0;

    WHILE cnt > 0 AND attempts < 50 DO
        SET candidate = CONCAT('SONG-', random_suffix(4));
        SELECT COUNT(*) INTO cnt FROM Song WHERE song_id = candidate;
        SET attempts = attempts + 1;
    END WHILE;

    IF cnt = 0 THEN
        RETURN candidate;
    END IF;

    RETURN CONCAT('SONG-', UNIX_TIMESTAMP());
END $$


-- Generate PLAYLIST ID
CREATE FUNCTION gen_playlist_id()
RETURNS VARCHAR(64)
DETERMINISTIC
BEGIN
    DECLARE candidate VARCHAR(64);
    DECLARE cnt INT DEFAULT 1;
    DECLARE attempts INT DEFAULT 0;

    WHILE cnt > 0 AND attempts < 50 DO
        SET candidate = CONCAT('PL_', random_suffix(8));
        SELECT COUNT(*) INTO cnt FROM Playlist WHERE playlist_id = candidate;
        SET attempts = attempts + 1;
    END WHILE;

    IF cnt = 0 THEN
        RETURN candidate;
    END IF;

    RETURN CONCAT('PL_', UNIX_TIMESTAMP());
END $$

DELIMITER ;
