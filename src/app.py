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

# Load environment
dotenv.load_dotenv()
PASSWORD = os.getenv("PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_NAME = os.getenv("DB_NAME", "oho")

init(autoreset=True)


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def spinner(text="Loading", duration=1.2):
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    end = time.time() + duration
    i = 0
    while time.time() < end:
        sys.stdout.write(f"\r{Fore.YELLOW}{text} {frames[i % len(frames)]}{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(0.06)
        i += 1
    sys.stdout.write("\r" + " " * (len(text) + 4) + "\r")
    sys.stdout.flush()

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
        print(df.to_string(index=False))
    print()
    pause_and_clear()


# DB CONFIG
DB_CONFIG = {
    "host": DB_HOST,
    "port": DB_PORT,
    "user": DB_USER,
    "password": PASSWORD,
    "database": DB_NAME
}


def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(Fore.RED + "Database connection error:", e)
        time.sleep(1.5)
        return None


def fetch_df(query, params=None, use_proc=False):
    """Return pandas DataFrame. If use_proc=True then query should be a (proc_name, params_tuple) pair."""
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        if use_proc:
            proc_name, proc_params = query
            cur.callproc(proc_name, proc_params or ())
            # fetch first resultset returned by procedure
            results = []
            cols = []
            for res in cur.stored_results():
                rows = res.fetchall()
                cols = res.column_names
                results = rows
                break
            df = pd.DataFrame(results, columns=cols) if results else pd.DataFrame(columns=cols)
        else:
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


def execute_proc(proc_name, params=None, commit=True):
    """Call a stored procedure that performs action(s). Returns affected rowcount where possible or -1 on error."""
    conn = get_connection()
    if not conn:
        return -1
    try:
        cur = conn.cursor()
        cur.callproc(proc_name, params or ())
        if commit:
            conn.commit()
        # Attempts to infer affected rows; mysql connector does not give rowcount for procedures reliably
        return 1
    except Error as e:
        print(Fore.RED + "DB Error (proc):", e)
        return -1
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass


def scalar_function_call(func_sql, params=None):
    """Call a function or expression that returns single scalar value. Example: SELECT GenerateUserID()"""
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute(func_sql, params or ())
        r = cur.fetchone()
        return r[0] if r else None
    except Error as e:
        print(Fore.RED + "DB Error (func):", e)
        return None
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass


# ---------- ID GENERATION (via DB functions) ----------
def generate_user_id():
    val = scalar_function_call("SELECT GenerateUserID()")
    return val or f"USER-{int(time.time())}"


def generate_artist_id():
    val = scalar_function_call("SELECT GenerateArtistID()")
    return val or f"ARTIST-{int(time.time())}"


def generate_song_id():
    val = scalar_function_call("SELECT GenerateSongID()")
    return val or f"SONG-{int(time.time())}"


def generate_playlist_id():
    # try DB function first, else fallback
    val = scalar_function_call("SELECT GeneratePlaylistID()")
    return val or f"PL_{int(time.time())}"


def generate_plan_id():
    val = scalar_function_call("SELECT GeneratePlanID()")
    return val or f"PLAN-{int(time.time())}"


# ---------- Application logic (CALLING stored procedures) ----------

# ---------- UI / Menus ---------- / Menus ----------

def startup_menu():
    while True:
        clear()
        print(Fore.CYAN + "===== MUSIC SYSTEM =====" + Style.RESET_ALL)
        print("1) Login as User")
        print("2) Admin (View Table Insights)")
        print("3) Exit")
        choice = input("Enter choice: ").strip()
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


# ---------- User flows (use stored procedures) ----------

def user_login():
    clear()
    user_id = input("Enter your User ID: ").strip()
    if not user_id:
        print(Fore.RED + "Empty input. Returning..." + Style.RESET_ALL)
        time.sleep(1)
        return

    spinner("Verifying user...")
    # assume procedure GetUserById returns a resultset with user details
    df = fetch_df(("GetUserById", (user_id,)), use_proc=True)
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
        choice = input("Choose: ").strip()
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
    df = fetch_df(("GetPlaylistsByUser", (user_id,)), use_proc=True)
    print_df(df, title=f"Playlists for {user_id}")


def add_playlist(user_id):
    clear()
    name = input("Enter new playlist name: ").strip()
    if not name:
        print(Fore.RED + "Playlist name cannot be empty." + Style.RESET_ALL)
        time.sleep(1)
        return
    playlist_id = generate_playlist_id()
    created_date = time.strftime("%Y-%m-%d")
    spinner("Creating playlist...")
    # Use stored procedure CreatePlaylist(user_id, playlist_id, playlist_name, created_date)
    res = execute_proc("CreatePlaylist", (user_id, playlist_id, name, created_date))
    if res >= 0:
        print(Fore.GREEN + f"Playlist '{name}' created (id={playlist_id})." + Style.RESET_ALL)
    else:
        print(Fore.RED + "Failed to create playlist." + Style.RESET_ALL)
    pause_and_clear()


def add_song_to_playlist(user_id):
    spinner("Loading your playlists...")
    p_df = fetch_df(("GetPlaylistsByUser", (user_id,)), use_proc=True)
    if p_df is None or p_df.empty:
        print(Fore.YELLOW + "You have no playlists. Create one first." + Style.RESET_ALL)
        time.sleep(1.2)
        return

    spinner("Loading songs...")
    songs_df = fetch_df(("GetAllSongs", ()), use_proc=True)
    if songs_df is None or songs_df.empty:
        print(Fore.YELLOW + "No songs in library." + Style.RESET_ALL)
        time.sleep(1.2)
        return

    clear()
    print(Fore.CYAN + "Your playlists:" + Style.RESET_ALL)
    print(p_df.to_string(index=False))
    chosen_pl = input("Enter playlist_id to add to: ").strip()
    if chosen_pl == "":
        print(Fore.RED + "Cancelled." + Style.RESET_ALL)
        time.sleep(1)
        return
    if chosen_pl not in set(p_df['playlist_id'].astype(str)):
        print(Fore.RED + "Invalid playlist id." + Style.RESET_ALL)
        time.sleep(1)
        return

    clear()
    print(Fore.CYAN + "Available songs:" + Style.RESET_ALL)
    print(songs_df.to_string(index=False))
    chosen_song = input("Enter song_id to add (or comma-separated multiple): ").strip()
    if not chosen_song:
        print(Fore.RED + "Cancelled." + Style.RESET_ALL)
        time.sleep(1)
        return
    song_ids = [s.strip() for s in chosen_song.split(",") if s.strip()]

    spinner("Adding songs...")
    added = 0
    for sid in song_ids:
        # Call stored procedure AddSongToPlaylist(playlist_id, song_id)
        res = execute_proc("AddSongToPlaylist", (chosen_pl, sid))
        if res >= 0:
            added += 1
    print(Fore.GREEN + f"Added {added} song(s) to playlist {chosen_pl}." + Style.RESET_ALL)
    pause_and_clear()


def delete_playlist(user_id):
    spinner("Fetching playlists...")
    p_df = fetch_df(("GetPlaylistsByUser", (user_id,)), use_proc=True)
    if p_df is None or p_df.empty:
        print(Fore.YELLOW + "No playlists to delete." + Style.RESET_ALL)
        time.sleep(1.2)
        return

    clear()
    print(Fore.CYAN + "Your playlists:" + Style.RESET_ALL)
    print(p_df.to_string(index=False))
    pid = input("Enter playlist_id to delete: ").strip()
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
    # Use procedure DeletePlaylist(playlist_id, user_id)
    res = execute_proc("DeletePlaylist", (pid, user_id))
    if res >= 0:
        print(Fore.GREEN + "Playlist deleted." + Style.RESET_ALL)
    else:
        print(Fore.RED + "Failed to delete (maybe it belongs to someone else)." + Style.RESET_ALL)
    pause_and_clear()


def view_followed_artists(user_id):
    spinner("Fetching followed artists...")
    df = fetch_df(("GetFollowedArtists", (user_id,)), use_proc=True)
    print_df(df, title=f"Artists followed by {user_id}")


def follow_unfollow(user_id):
    spinner("Loading artists...")
    all_artists = fetch_df(("GetAllArtists", ()), use_proc=True)
    if all_artists is None or all_artists.empty:
        print(Fore.YELLOW + "No artists in system." + Style.RESET_ALL)
        time.sleep(1)
        return

    follows = fetch_df(("GetFollowedArtistIds", (user_id,)), use_proc=True)
    followed_set = set()
    if follows is not None and not follows.empty:
        followed_set = set(follows['artist_id'].astype(str))

    clear()
    print(Fore.CYAN + "Artists (F = you follow):" + Style.RESET_ALL)
    display_rows = []
    for _, r in all_artists.iterrows():
        aid = str(r['artist_id'])
        display_rows.append({
            "artist_id": aid,
            "name": f"{r.get('first_name','') or ''} {r.get('last_name','') or ''}".strip(),
            "followed": ("F" if aid in followed_set else "")
        })
    df_display = pd.DataFrame(display_rows)
    print(df_display.to_string(index=False))

    cmd = input("Commands: [f]ollow <artist_id>, [u]nfollow <artist_id>, [b]ackEnter: ").strip().split()
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
        res = execute_proc("FollowArtist", (user_id, aid))
        if res >= 0:
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
        res = execute_proc("UnfollowArtist", (user_id, aid))
        if res >= 0:
            print(Fore.GREEN + "Unfollowed." + Style.RESET_ALL)
        else:
            print(Fore.RED + "Failed to unfollow." + Style.RESET_ALL)
        pause_and_clear()
    else:
        if len(cmd) == 1 and cmd[0].lower() == 'b':
            return
        print(Fore.YELLOW + "Unknown command." + Style.RESET_ALL)
        time.sleep(1)


# ---------- Admin flows (procedures) ----------

def admin_menu():
    while True:
        clear()
        print(Fore.MAGENTA + "===== ADMIN PANEL =====" + Style.RESET_ALL)
        print("1) Artists sorted by number of followers")
        print("2) Users with most playlists")
        print("3) View any table (pandas)")
        print("4) Extra insights (creative)")
        print("5) Back")
        choice = input("Choose: ").strip()
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
    df = fetch_df(("Admin_TopArtists", ()), use_proc=True)
    print_df(df, title="Artists by followers (desc)")


def admin_users_most_playlists():
    spinner("Counting playlists per user...")
    df = fetch_df(("Admin_UsersMostPlaylists", ()), use_proc=True)
    print_df(df, title="Users with most playlists (desc)")


def admin_view_table():
    clear()
    table = input("Enter table name (Advertisement, Artist, Composes, Enrolls, Follows, Free, Gets, Plan, Playlist, Song, SongsInPlaylist, User): ").strip()
    if not table:
        return
    allowed = {"Advertisement","Artist","Composes","Enrolls","Follows","Free","Gets","Plan","Playlist","Song","SongsInPlaylist","User"}
    if table not in allowed:
        print(Fore.RED + "Table not recognized or not allowed." + Style.RESET_ALL)
        time.sleep(1)
        return
    spinner("Fetching table...")
    # Expecting Admin_ViewTable to accept a table name and return rows
    df = fetch_df(("Admin_ViewTable", (table,)), use_proc=True)
    print_df(df, title=f"Table: {table}")


def admin_creative_insights():
    spinner("Crunching some creative insights...")
    g1 = fetch_df(("Admin_TopGenres", ()), use_proc=True)
    if g1 is not None and not g1.empty:
        print_df(g1, title="Top genres by number of songs")

    g2 = fetch_df(("Admin_UsersWithMostFollows", ()), use_proc=True)
    if g2 is not None and not g2.empty:
        print_df(g2, title="Users who follow the most artists")

    avg_df = fetch_df(("Admin_AvgPlaylists", ()), use_proc=True)
    if avg_df is not None and not avg_df.empty:
        print_df(avg_df, title="Average playlists per user (only users who have >=1 playlist)")


# ---------- Entry point ----------
if __name__ == "__main__":
    try:
        startup_menu()
    except KeyboardInterrupt:
        clear()
        print("" + Fore.YELLOW + "Interrupted. Bye!" + Style.RESET_ALL)
        sys.exit(0)
