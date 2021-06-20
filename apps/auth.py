import re
from datetime import datetime

from bottle import Bottle, request, abort
from bottlejwt import JwtPlugin

from utils import sql

auth_subapp = Bottle()

@auth_subapp.post("/login")
def login(db):
    username, password = request.json["username"], request.json["password"]
    if sql.check_credentials(db, username, password):
        user = sql.get_user(db, username)
        jwt: str = JwtPlugin.encode({"uid": user["id"], "username": user["username"], "nickname": user["nickname"], "timestamp": datetime.now().isoformat()})
        return {"token": jwt}
    abort(401, "Username/password mismatch")

@auth_subapp.post("/register")
def register(db):
    username, nickname, password = request.json["username"], request.json["nickname"], request.json["password"]
    if len(username) < 3:
        abort(400, "Username must have 3 or more character")
    if not re.match(r"[A-Za-z_].*", username):
        abort(400, "Username must start with alphabet character or underline (_)")
    if not re.match(r"[A-Za-z]\w+", username):
        abort(400, "Username must only contain alphanumeric character and underline (_)")
    if not sql.add_user(db, username, nickname, password):
        abort(403, "Username already exists")

@auth_subapp.route("/password", method="PATCH", auth="_")
def set_password(db, auth):
    password = request.json["password"]
    sql.set_password(db, auth["uid"], password)
