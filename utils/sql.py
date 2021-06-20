from sqlite3 import Connection
from hashlib import sha256


def get_config(db: Connection, name: str):
    return db.execute("SELECT value FROM config WHERE name = ?", (name,)).fetchone()["value"]

def get_user(db: Connection, username: str) -> dict:
    user = db.execute("SELECT id, username, nickname FROM user WHERE username = ?", (username,)).fetchone()
    if user is None: return None
    user_dict = dict(user)
    return user_dict

def get_user_id(db: Connection, username: str) -> int:
    user = db.execute("SELECT id FROM user WHERE username = ?", (username,)).fetchone()
    if user is None: return None
    return user["id"]

def add_user(db: Connection, username: str, nickname: str, password: str):
    password_salt = get_config(db, "password_salt")
    password_hash = sha256((password + password_salt).encode()).hexdigest()
    return db.execute("INSERT OR IGNORE INTO user (username, nickname, password_hash) VALUES (?, ?, ?)", (username, nickname, password_hash)).rowcount

def set_password(db: Connection, uid: int, password: str):
    password_salt = get_config(db, "password_salt")
    password_hash = sha256((password + password_salt).encode()).hexdigest()
    return db.execute("UPDATE user set password_hash = ? WHERE id = ?", (password_hash , uid)).rowcount

def get_avatar(db: Connection, uid: int) -> bytes:
    return db.execute("SELECT avatar FROM user WHERE id = ?", (uid ,)).fetchone()["avatar"]

def get_avatar_by_username(db: Connection, username: str) -> bytes:
    return db.execute("SELECT avatar FROM user WHERE username = ?", (username ,)).fetchone()["avatar"]

def set_nickname(db: Connection, uid: int, nickname: str):
    return db.execute("UPDATE user SET nickname = ? WHERE id = ?", (nickname, uid)).rowcount

def set_avatar(db: Connection, uid: int, avatar: bytes):
    return db.execute("UPDATE user SET avatar = ? WHERE id = ?", (avatar, uid)).rowcount

def del_avatar(db: Connection, uid: int):
    return db.execute("UPDATE user SET avatar = NULL WHERE id = ?", (uid ,)).rowcount

def check_credentials(db: Connection, username: str, password: str) -> bool:
    password_salt = get_config(db, "password_salt")
    password_hash = db.execute("SELECT password_hash FROM user WHERE username = ?", (username ,)).fetchone()["password_hash"]
    input_hash = sha256((password + password_salt).encode()).hexdigest()
    return input_hash == password_hash

def add_post(db: Connection, uid: int, content: str):
    return db.execute("INSERT INTO posts (uid, content, date) VALUES (?, ?, CURRENT_TIMESTAMP)", (uid, content)).lastrowid

def add_reply(db: Connection, uid: int, content: str, reply_to: int):
    return db.execute("INSERT INTO posts (uid, content, date, reply_to) VALUES (?, ?, CURRENT_TIMESTAMP, ?)", (uid, content, reply_to)).lastrowid

def get_timeline(db: Connection, uid: int, offset: int=0):
    timeline = db.execute(
        (
        "SELECT user.username, user.nickname, posts.*, COUNT(replies.id) AS replies_count, COUNT(fav.uid) AS fav_count FROM follows "
        "INNER JOIN user ON user.id = posts.uid "
        "INNER JOIN posts ON follows.follows_uid = posts.uid "
        "LEFT JOIN fav ON fav.post_id = posts.id "
        "LEFT JOIN posts AS replies ON replies.reply_to = posts.id "
        "WHERE follows.uid = ? GROUP BY posts.id ORDER BY posts.date DESC LIMIT %d,50"
        ) % offset
        , (uid ,)
    ).fetchall()
    return {"timeline": [dict(row) for row in timeline]}

def get_user_timeline(db: Connection, username: str, offset: int=0):
    timeline = db.execute(
        (
        "SELECT user.username, user.nickname, posts.*, COUNT(replies.id) AS replies_count, COUNT(fav.uid) AS fav_count FROM posts"
        " INNER JOIN user ON user.id = posts.uid "
        "LEFT JOIN fav ON fav.post_id = posts.id "
        "LEFT JOIN posts AS replies ON replies.reply_to = posts.id "
        "WHERE username = ? GROUP BY posts.id ORDER BY posts.date DESC LIMIT %d,50"
        ) % offset
        , (username ,)
    ).fetchall()
    return {"timeline": [dict(row) for row in timeline]}

def get_following(db: Connection, uid: int):
    following = db.execute(
        (
        "SELECT user.username, user.nickname, follows.follows_uid FROM follows"
        " INNER JOIN user ON user.id = follows.follows_uid WHERE follows.uid = ?"
        )
        , (uid ,)
    ).fetchall()
    return {"following": [dict(row) for row in following]}

def get_followers(db: Connection, uid: int):
    followers = db.execute(
        (
        "SELECT user.username, user.nickname, follows.follows_uid FROM follows"
        " INNER JOIN user ON user.id = follows.uid WHERE follows.follows_uid = ?"
        )
        , (uid ,)
    ).fetchall()
    return {"followers": [dict(row) for row in followers]}

def add_follows(db: Connection, uid: int, follows_uid: int) -> bool:
    return db.execute("INSERT OR IGNORE INTO follows (uid, follows_uid) VALUES (?, ?)", (uid, follows_uid)).rowcount

def del_follows(db: Connection, uid: int, follows_uid: int) -> bool:
    return db.execute("DELETE FROM follows WHERE uid = ? AND follows_uid = ?", (uid, follows_uid)).rowcount

def get_post(db: Connection, post_id: int):
    post = db.execute(
        (
        "SELECT user.username, user.nickname, posts.id, posts.uid, posts.content, posts.date FROM posts"
        " INNER JOIN user ON user.id = posts.uid WHERE posts.id = ? ORDER BY posts.date ORDER BY posts.date DESC"
        )
        , (post_id ,)
    ).fetchone()
    if post is None: return None
    return dict(post)

def pre_del_post_get_uid(db: Connection, post_id: int):
    uid = db.execute(
        "SELECT uid FROM posts WHERE id = ?"
        , (post_id ,)
    ).fetchone()
    if uid is None: return None
    return uid["uid"]

def del_post_check_uid(db: Connection, post_id: int, uid: int) -> bool:
    return db.execute(
        "DELETE FROM posts WHERE id = ? AND uid = ?"
        , (post_id , uid)
    ).rowcount

def get_post_response(db: Connection, post_id: int):
    responses = db.execute(
        (
        "SELECT user.username, user.nickname, posts.id, posts.uid, posts.content, posts.date FROM posts"
        " INNER JOIN user ON user.id = posts.uid WHERE posts.reply_to = ? ORDER BY posts.date DESC"
        )
        , (post_id ,)
    ).fetchall()
    return {"responses": [dict(row) for row in responses]}

def get_user_fav(db: Connection, uid: int):
    fav = db.execute(
        (
            "SELECT user.username, user.nickname, posts.* FROM fav INNER JOIN posts ON posts.id = fav.post_id "
            "INNER JOIN user ON user.id = posts.uid "
            "WHERE fav.uid = ? ORDER BY fav.timestamp DESC"
        )
        , (uid, )
    ).fetchall()
    return {"fav": [dict(row) for row in fav]}

def add_user_fav(db: Connection, uid: int, post_id: int) -> bool:
    return db.execute("INSERT OR IGNORE INTO fav (uid, post_id) VALUES (?, ?)", (uid, post_id)).rowcount

def del_user_fav(db: Connection, uid: int, post_id: int) -> bool:
    return db.execute("DELETE FROM fav WHERE uid = ? AND post_id = ?", (uid, post_id)).rowcount

def get_user_fav_by_username(db: Connection, username: str):
    fav = db.execute(
        (
            "SELECT poster.username, poster.nickname, posts.* FROM fav INNER JOIN posts ON posts.id = fav.post_id "
            "INNER JOIN user ON user.id = fav.uid "
            "INNER JOIN user AS poster ON poster.id = posts.uid "
            "WHERE user.username = ? ORDER BY fav.timestamp DESC"
        )
        , (username, )
    ).fetchall()
    return {"fav": [dict(row) for row in fav]}

