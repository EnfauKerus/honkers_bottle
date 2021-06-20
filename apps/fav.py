from bottle import Bottle, abort

from utils import sql

fav = Bottle()

@fav.get("/you", auth="_")
def get_fav(db, auth):
    return sql.get_user_fav(db, auth["uid"])

@fav.get("/user/<username>")
def get_fav_username(username, db):
    return sql.get_user_fav_by_username(db, username)

@fav.get("/post/<post_id:int>", auth="_")
def check_fav(post_id, db, auth):
    if not sql.check_user_fav(db, auth["uid"], post_id):
        abort(404, "Not favorited")

@fav.post("/post/<post_id:int>", auth="_")
def add_fav(post_id, db, auth):
    if not sql.add_user_fav(db, auth["uid"], post_id):
        abort(400, "Already added or post does not exist")

@fav.delete("/post/<post_id:int>", auth="_")
def del_fav(post_id, db, auth):
    sql.del_user_fav(db, auth["uid"], post_id)

