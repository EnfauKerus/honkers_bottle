from bottle import Bottle, request, abort

from utils import sql

timeline = Bottle()

@timeline.get("/following", auth="_")
def get_timeline(db, auth):
    return sql.get_timeline(db, auth["uid"])

@timeline.get("/of/<username>")
def get_user_timeline(username, db):
    return sql.get_user_timeline(db, username)

@timeline.post("/post", auth="_")
def add_post(db, auth):
    post_id = sql.add_post(db, auth["uid"], request.json["content"])
    return {"id": post_id, "content": request.json["content"]}


@timeline.delete("/<post_id:int>", auth="_")
def del_post(post_id, db, auth):
    uid = sql.pre_del_post_get_uid(db, post_id)
    if uid != auth["uid"]: abort(403, "You do not own this post.")
    success = sql.del_post_check_uid(db, post_id, auth["uid"])
    if not success: abort(404, "No such post")
    return {"status": "Deleted"}

@timeline.get("/<post_id:int>/responses")
def get_post_responses(post_id, db):
    post = sql.get_post(db, post_id)
    if post is None: abort(404, "No such post")
    return sql.get_post_response(db, post_id)

@timeline.post("/<post_id:int>/responses", auth="_")
def add_post_responses(post_id, db, auth):
    post = sql.get_post(db, post_id)
    if post is None: abort(404, "No such post")
    reply_id = sql.add_reply(db, auth["uid"], request.json["content"], post_id)
    return {"id": reply_id, "content": request.json["content"], "reply_to": post_id}
