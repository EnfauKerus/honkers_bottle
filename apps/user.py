from io import BytesIO

from bottle import Bottle, request, response, abort
from PIL import Image, UnidentifiedImageError

from utils import sql

user = Bottle()

@user.get("/<username>", auth="_")
def get_user(username, db):
    return sql.get_user(db, username)

@user.get("/<username>/avatar")
def get_user_avatar(username, db):
    avatar = sql.get_avatar_by_username(db, username)
    if avatar is None:
        return abort(404, "No avatar")
    response.content_type = "image/jpeg"
    return avatar

@user.post("/<username>/avatar", auth="_")
def post_avatar(username, db, auth):
    if username != auth["username"]: abort(403, "Forbidden")
    if request.content_length == 0: abort(400, "No content")
    try:
        img: Image = Image.open(request.body)
        img.thumbnail((256, 256))
        avatar: BytesIO = BytesIO()
        img.save(avatar, "JPEG", quality=75)
        avatar_bytes = avatar.getvalue()
        sql.set_avatar(db, auth["uid"], avatar_bytes)
        avatar.close()
        return {"size": len(avatar_bytes)}
    except UnidentifiedImageError:
        abort(400, "Invalid format")

@user.delete("/<username>/avatar", auth="_")
def delete_avatar(username, db, auth):
    if username != auth["username"]: abort(403, "Forbidden")
    sql.del_avatar(db, auth["uid"])
