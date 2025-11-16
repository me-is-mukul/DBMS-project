import mysql.connector
from mysql.connector import Error
import pandas as pd
import time
import os
import sys
import random
import string
from colorama import Fore, Style, init
import dotenv

dotenv.load_dotenv()
PASSWORD = os.getenv("PASSWORD")

init(autoreset=True)

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def spinner(text="Loading", duration=1.5):
    """A slightly nicer blocking spinner. duration in seconds."""
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    end = time.time() + duration
    i = 0
    while time.time() < end:
        sys.stdout.write(f"\r{Fore.YELLOW}{text} {frames[i % len(frames)]}{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    sys.stdout.write("\r" + " " * (len(text) + 6) + "\r")


def pause_and_clear(msg="Press Enter to continue..."):
    input(msg)
    clear()


def print_df(df, title=None):
    clear()
    if title:
        print(Fore.CYAN + title + Style.RESET_ALL)
    if df is None or df.empty:
        print(Fore.YELLOW + "No records found." + Style.RESET_ALL)
    else:
        # Show as a neat pandas table
        print(df.to_string(index=False))
    print()
    pause_and_clear()


# DB HELPERS
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": PASSWORD,
    "database": "oho"
}


def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(Fore.RED + "Database connection error:", e)
        time.sleep(1.5)
        return None


def fetch_df(query, params=None):
    """Return a pandas DataFrame for a SELECT query, or None on error."""
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute(query, params or ())
        cols = cur.column_names
        rows = cur.fetchall()
        df = pd.DataFrame(rows, columns=cols)
        return df
    except Error as e:
        print(Fore.RED + "DB Error:", e)
        time.sleep(1.2)
        return None
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass


def execute_query(query, params=None, commit=True):
    """Execute INSERT/UPDATE/DELETE. Returns affected rows or -1 on error."""
    conn = get_connection()
    if not conn:
        return -1
    try:
        cur = conn.cursor()
        cur.execute(query, params or ())
        if commit:
            conn.commit()
        affected = cur.rowcount
        return affected
    except Error as e:
        print(Fore.RED + "DB Error:", e)
        return -1
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass


# -ID GENERATION HELPERS -
def generate_suffix(length=4):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def unique_id_for(table, id_col, prefix, suffix_len=4):
    """
    prefix = full text prefix (e.g., 'USER-', 'ARTIST-', 'PLAYLIST-')
    suffix_len = length of random alphanumeric part
    """
    for _ in range(50):
        candidate = prefix + generate_suffix(suffix_len)
        df = fetch_df(f"SELECT {id_col} FROM {table} WHERE {id_col} = %s", (candidate,))
        if df is None or df.empty:
            return candidate

    return prefix + str(int(time.time()))


# ---------- Specific ID functions ----------
def generate_user_id():
    return unique_id_for("User", "user_id", "USER-", 4)

def generate_artist_id():
    return unique_id_for("Artist", "artist_id", "ARTIST-", 4)

def generate_song_id():
    return unique_id_for("Song", "song_id", "SONG-", 4)

def generate_playlist_id():
    return unique_id_for("Playlist", "playlist_id", "PLAYLIST-", 4)

def generate_plan_id():
    # If plan IDs are like PLAN-1, PLAN-2, etc.
    for _ in range(50):
        num = random.randint(1, 999)
        candidate = f"PLAN-{num}"
        df = fetch_df("SELECT plan_id FROM Plan WHERE plan_id=%s", (candidate,))
        if df is None or df.empty:
            return candidate

    return f"PLAN-{int(time.time())}"

# ---------- Startup menu ----------
def startup_menu():
    while True:
        clear()
        print(Fore.CYAN + "===== KIWI MUSIC SYSTEM =====" + Style.RESET_ALL)
        print("1) Login as User")
        print("2) Admin (View Table Insights)")
        print("3) Exit")
        choice = input("\nEnter choice: ").strip()
        if choice == "1":
            user_login()
        elif choice == "2":
            admin_menu()
        elif choice == "3":
            clear()
            print(Fore.GREEN + "Goodbye!" + Style.RESET_ALL)
            sys.exit(0)
        else:
            print(Fore.RED + "Invalid choice!" + Style.RESET_ALL)
            time.sleep(1)


# ---------- User flows ----------
def user_login():
    clear()
    user_id = input("Enter your User ID: ").strip()
    if not user_id:
        print(Fore.RED + "Empty input. Returning..." + Style.RESET_ALL)
        time.sleep(1)
        return

    spinner("Verifying user...")
    df = fetch_df("SELECT * FROM `User` WHERE user_id = %s", (user_id,))
    if df is None or df.empty:
        print(Fore.RED + "User not found!" + Style.RESET_ALL)
        time.sleep(1.2)
        return
    user_menu(user_id)


def user_menu(user_id):
    while True:
        clear()
        print(Fore.GREEN + f"===== Welcome, {user_id} =====" + Style.RESET_ALL)
        print("1) View my playlists")
        print("2) Add new playlist")
        print("3) Add songs to playlist")
        print("4) Delete playlist")
        print("5) View followed artists")
        print("6) Follow/unfollow artist")
        print("7) Logout")
        choice = input("\nChoose: ").strip()
        if choice == "1":
            view_playlists(user_id)
        elif choice == "2":
            add_playlist(user_id)
        elif choice == "3":
            add_song_to_playlist(user_id)
        elif choice == "4":
            delete_playlist(user_id)
        elif choice == "5":
            view_followed_artists(user_id)
        elif choice == "6":
            follow_unfollow(user_id)
        elif choice == "7":
            return
        else:
            print(Fore.RED + "Invalid choice!" + Style.RESET_ALL)
            time.sleep(1)


def view_playlists(user_id):
    spinner("Fetching playlists...")
    df = fetch_df(
        "SELECT playlist_id, playlist_name, created_date FROM Playlist WHERE user_id=%s ORDER BY created_date DESC",
        (user_id,)
    )
    print_df(df, title=f"Playlists for {user_id}")


def add_playlist(user_id):
    clear()
    name = input("Enter new playlist name: ").strip()
    if not name:
        print(Fore.RED + "Playlist name cannot be empty." + Style.RESET_ALL)
        time.sleep(1)
        return
    playlist_id = unique_id_for("Playlist", "playlist_id", "PL_", length=8)
    created_date = time.strftime("%Y-%m-%d")
    spinner("Creating playlist...")
    rows = execute_query(
        "INSERT INTO Playlist (playlist_id, playlist_name, created_date, user_id) VALUES (%s, %s, %s, %s)",
        (playlist_id, name, created_date, user_id)
    )
    if rows > 0:
        print(Fore.GREEN + f"Playlist '{name}' created (id={playlist_id})." + Style.RESET_ALL)
    else:
        print(Fore.RED + "Failed to create playlist." + Style.RESET_ALL)
    pause_and_clear()


def add_song_to_playlist(user_id):
    # show user's playlists
    spinner("Loading your playlists...")
    p_df = fetch_df("SELECT playlist_id, playlist_name FROM Playlist WHERE user_id=%s", (user_id,))
    if p_df is None or p_df.empty:
        print(Fore.YELLOW + "You have no playlists. Create one first." + Style.RESET_ALL)
        time.sleep(1.2)
        return

    # show available songs
    spinner("Loading songs...")
    songs_df = fetch_df("SELECT song_id, name, genre FROM Song ORDER BY name")
    if songs_df is None or songs_df.empty:
        print(Fore.YELLOW + "No songs in library." + Style.RESET_ALL)
        time.sleep(1.2)
        return

    # Display playlists
    clear()
    print(Fore.CYAN + "Your playlists:" + Style.RESET_ALL)
    print(p_df.to_string(index=False))
    chosen_pl = input("\nEnter playlist_id to add to: ").strip()
    if chosen_pl == "":
        print(Fore.RED + "Cancelled." + Style.RESET_ALL)
        time.sleep(1)
        return
    if chosen_pl not in set(p_df['playlist_id'].astype(str)):
        print(Fore.RED + "Invalid playlist id." + Style.RESET_ALL)
        time.sleep(1)
        return

    # Display songs
    clear()
    print(Fore.CYAN + "Available songs:" + Style.RESET_ALL)
    print(songs_df.to_string(index=False))
    chosen_song = input("\nEnter song_id to add (or comma-separated multiple): ").strip()
    if not chosen_song:
        print(Fore.RED + "Cancelled." + Style.RESET_ALL)
        time.sleep(1)
        return
    song_ids = [s.strip() for s in chosen_song.split(",") if s.strip()]

    spinner("Adding songs...")
    added = 0
    for sid in song_ids:
        # validate song exists
        df_check = fetch_df("SELECT song_id FROM Song WHERE song_id=%s", (sid,))
        if df_check is None or df_check.empty:
            print(Fore.YELLOW + f"Song id {sid} not found. Skipping." + Style.RESET_ALL)
            continue
        # avoid duplicates
        df_dup = fetch_df("SELECT song_id FROM SongsInPlaylist WHERE playlist_id=%s AND song_id=%s", (chosen_pl, sid))
        if df_dup is not None and not df_dup.empty:
            print(Fore.YELLOW + f"Song {sid} already in playlist {chosen_pl}. Skipping." + Style.RESET_ALL)
            continue
        rows = execute_query(
            "INSERT INTO SongsInPlaylist (playlist_id, song_id) VALUES (%s, %s)",
            (chosen_pl, sid)
        )
        if rows > 0:
            added += 1

    print(Fore.GREEN + f"Added {added} song(s) to playlist {chosen_pl}." + Style.RESET_ALL)
    pause_and_clear()


def delete_playlist(user_id):
    spinner("Fetching playlists...")
    p_df = fetch_df("SELECT playlist_id, playlist_name FROM Playlist WHERE user_id=%s", (user_id,))
    if p_df is None or p_df.empty:
        print(Fore.YELLOW + "No playlists to delete." + Style.RESET_ALL)
        time.sleep(1.2)
        return

    clear()
    print(Fore.CYAN + "Your playlists:" + Style.RESET_ALL)
    print(p_df.to_string(index=False))
    pid = input("\nEnter playlist_id to delete: ").strip()
    if not pid:
        print(Fore.RED + "Cancelled." + Style.RESET_ALL)
        time.sleep(1)
        return
    if pid not in set(p_df['playlist_id'].astype(str)):
        print(Fore.RED + "Invalid playlist id." + Style.RESET_ALL)
        time.sleep(1)
        return

    confirm = input(Fore.RED + f"Are you sure you want to delete playlist {pid}? (y/N): " + Style.RESET_ALL).lower()
    if confirm != "y":
        print("Aborted.")
        time.sleep(0.6)
        return

    spinner("Deleting playlist data...")
    # delete songs in playlist then playlist
    execute_query("DELETE FROM SongsInPlaylist WHERE playlist_id=%s", (pid,))
    rows = execute_query("DELETE FROM Playlist WHERE playlist_id=%s AND user_id=%s", (pid, user_id))
    if rows > 0:
        print(Fore.GREEN + "Playlist deleted." + Style.RESET_ALL)
    else:
        print(Fore.RED + "Failed to delete (maybe it belongs to someone else)." + Style.RESET_ALL)
    pause_and_clear()


def view_followed_artists(user_id):
    spinner("Fetching followed artists...")
    df = fetch_df("""
        SELECT a.artist_id, a.first_name, a.last_name
        FROM Artist a
        JOIN Follows f ON a.artist_id = f.artist_id
        WHERE f.user_id = %s
        ORDER BY a.last_name, a.first_name
    """, (user_id,))
    print_df(df, title=f"Artists followed by {user_id}")


def follow_unfollow(user_id):
    # list all artists
    spinner("Loading artists...")
    all_artists = fetch_df("SELECT artist_id, first_name, last_name FROM Artist ORDER BY last_name, first_name")
    if all_artists is None or all_artists.empty:
        print(Fore.YELLOW + "No artists in system." + Style.RESET_ALL)
        time.sleep(1)
        return

    # show which ones user follows
    follows = fetch_df("SELECT artist_id FROM Follows WHERE user_id=%s", (user_id,))
    followed_set = set()
    if follows is not None:
        followed_set = set(follows['artist_id'].astype(str))

    clear()
    print(Fore.CYAN + "Artists (F = you follow):" + Style.RESET_ALL)
    # create display
    display_rows = []
    for _, r in all_artists.iterrows():
        aid = str(r['artist_id'])
        display_rows.append({
            "artist_id": aid,
            "name": f"{r['first_name'] or ''} {r['last_name'] or ''}".strip(),
            "followed": ("F" if aid in followed_set else "")
        })
    df_display = pd.DataFrame(display_rows)
    print(df_display.to_string(index=False))

    cmd = input("\nCommands: [f]ollow <artist_id>, [u]nfollow <artist_id>, [b]ack\nEnter: ").strip().split()
    if not cmd:
        return
    op = cmd[0].lower()
    if op in ("f", "follow") and len(cmd) >= 2:
        aid = cmd[1]
        if aid in followed_set:
            print(Fore.YELLOW + "Already following." + Style.RESET_ALL)
            time.sleep(1)
            return
        spinner("Following artist...")
        rows = execute_query("INSERT INTO Follows (user_id, artist_id) VALUES (%s, %s)", (user_id, aid))
        if rows > 0:
            print(Fore.GREEN + "Now following." + Style.RESET_ALL)
        else:
            print(Fore.RED + "Failed to follow. Check artist id." + Style.RESET_ALL)
        pause_and_clear()
    elif op in ("u", "unfollow") and len(cmd) >= 2:
        aid = cmd[1]
        if aid not in followed_set:
            print(Fore.YELLOW + "You do not follow that artist." + Style.RESET_ALL)
            time.sleep(1)
            return
        spinner("Unfollowing artist...")
        rows = execute_query("DELETE FROM Follows WHERE user_id=%s AND artist_id=%s", (user_id, aid))
        if rows > 0:
            print(Fore.GREEN + "Unfollowed." + Style.RESET_ALL)
        else:
            print(Fore.RED + "Failed to unfollow." + Style.RESET_ALL)
        pause_and_clear()
    else:
        # fallback: allow user to type artist id to toggle
        if len(cmd) == 1 and cmd[0].lower() == 'b':
            return
        print(Fore.YELLOW + "Unknown command." + Style.RESET_ALL)
        time.sleep(1)


# ---------- Admin flows ----------
def admin_menu():
    while True:
        clear()
        print(Fore.MAGENTA + "===== ADMIN PANEL =====" + Style.RESET_ALL)
        print("1) Artists sorted by number of followers")
        print("2) Users with most playlists")
        print("3) View any table (pandas)")
        print("4) Extra insights (creative)")
        print("5) Back")
        choice = input("\nChoose: ").strip()
        if choice == "1":
            admin_top_artists()
        elif choice == "2":
            admin_users_most_playlists()
        elif choice == "3":
            admin_view_table()
        elif choice == "4":
            admin_creative_insights()
        elif choice == "5":
            return
        else:
            print(Fore.RED + "Invalid choice!" + Style.RESET_ALL)
            time.sleep(1)


def admin_top_artists():
    spinner("Aggregating followers...")
    df = fetch_df("""
        SELECT a.artist_id,
               CONCAT(IFNULL(a.first_name, ''), ' ', IFNULL(a.last_name, '')) AS artist_name,
               COUNT(f.user_id) AS follower_count
        FROM Artist a
        LEFT JOIN Follows f ON a.artist_id = f.artist_id
        GROUP BY a.artist_id
        ORDER BY follower_count DESC, artist_name
        LIMIT 100
    """)
    print_df(df, title="Artists by followers (desc)")


def admin_users_most_playlists():
    spinner("Counting playlists per user...")
    df = fetch_df("""
        SELECT u.user_id,
               CONCAT(u.first_name, ' ', IFNULL(u.second_name, '')) AS user_name,
               COUNT(p.playlist_id) AS playlist_count
        FROM `User` u
        LEFT JOIN Playlist p ON u.user_id = p.user_id
        GROUP BY u.user_id
        ORDER BY playlist_count DESC, user_name
        LIMIT 100
    """)
    print_df(df, title="Users with most playlists (desc)")


def admin_view_table():
    clear()
    table = input("Enter table name (Advertisement, Artist, Composes, Enrolls, Follows, Free, Gets, Plan, Playlist, Song, SongsInPlaylist, User): ").strip()
    if not table:
        return
    # Basic validation
    allowed = {"Advertisement","Artist","Composes","Enrolls","Follows","Free","Gets","Plan","Playlist","Song","SongsInPlaylist","User"}
    if table not in allowed:
        print(Fore.RED + "Table not recognized or not allowed." + Style.RESET_ALL)
        time.sleep(1)
        return
    spinner("Fetching table...")
    df = fetch_df(f"SELECT * FROM `{table}` LIMIT 1000")
    print_df(df, title=f"Table: {table}")


def admin_creative_insights():
    spinner("Crunching some creative insights...")
    # Example extra insights:
    # - Top genres by number of songs
    # - Users who follow the most artists
    # - Average playlists per user (excluding zero)
    insights = []

    g1 = fetch_df("""
        SELECT genre, COUNT(*) AS song_count
        FROM Song
        WHERE genre IS NOT NULL AND genre <> ''
        GROUP BY genre
        ORDER BY song_count DESC
        LIMIT 10
    """)
    if g1 is not None and not g1.empty:
        print_df(g1, title="Top genres by number of songs")

    g2 = fetch_df("""
        SELECT u.user_id, CONCAT(u.first_name,' ',IFNULL(u.second_name,'')) AS name, COUNT(f.artist_id) AS follows
        FROM `User` u
        LEFT JOIN Follows f ON u.user_id = f.user_id
        GROUP BY u.user_id
        ORDER BY follows DESC
        LIMIT 20
    """)
    if g2 is not None and not g2.empty:
        print_df(g2, title="Users who follow the most artists")

    # average playlists per user (report)
    avg_df = fetch_df("""
        SELECT ROUND(AVG(cnt),2) AS avg_playlists_per_user
        FROM (
            SELECT COUNT(*) AS cnt FROM Playlist GROUP BY user_id
        ) t
    """)
    if avg_df is not None and not avg_df.empty:
        print_df(avg_df, title="Average playlists per user (only users who have >=1 playlist)")

# ---------- Entry point ----------
if __name__ == "__main__":
    try:
        startup_menu()
    except KeyboardInterrupt:
        clear()
        print("\n" + Fore.YELLOW + "Interrupted. Bye!" + Style.RESET_ALL)
        sys.exit(0)
