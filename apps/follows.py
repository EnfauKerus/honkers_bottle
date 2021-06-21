from bottle import Bottle, abort

from utils import sql

follows = Bottle()

@follows.get("/following/<username>")
def get_following(username, db):
    uid = sql.get_user_id(db, username)
    if uid:
        return sql.get_following(db, uid)
    else:
        abort(404, "No such user")

@follows.get("/followers/<username>")
def get_followers(username, db):
    uid = sql.get_user_id(db, username)
    if uid:
        return sql.get_followers(db, uid)
    else:
        abort(404, "No such user")

@follows.get("/follow", auth="_")
def get_follow(db, auth):
    return sql.get_following(db, auth["uid"])

@follows.get("/follow/<username>", auth="_")
def check_follow(username, db, auth):
    follows_uid = sql.get_user_id(db, username)
    if follows_uid:
        if not sql.check_following(db, auth["uid"], follows_uid):
            abort(400, "Not following")
    else:
        abort(404, "No such user")

@follows.post("/follow/<username>", auth="_")
def add_follow(username, db, auth):
    follows_uid = sql.get_user_id(db, username)
    if follows_uid:
        if not sql.add_follows(db, auth["uid"], follows_uid):
            abort(400, "Already followed")
    else:
        abort(404, "No such user")

@follows.delete("/follow/<username>", auth="_")
def del_follow(username, db, auth):
    follows_uid = sql.get_user_id(db, username)
    if follows_uid:
        if follows_uid == auth["uid"]:
            abort(400, "Can't unfollow yourself")
        if not sql.del_follows(db, auth["uid"], follows_uid):
            abort(400, "Already unfollowed")
    else:
        abort(404, "No such user")
