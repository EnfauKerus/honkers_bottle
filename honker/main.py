from bottle import Bottle
from bottle_sqlite import SQLitePlugin
from bottlejwt import JwtPlugin

import apps

from utils import random_str, set_err_handler

root = Bottle()

def validation(auth, auth_value):
    return True
root.mount("/auth", apps.auth)
root.mount("/fav", apps.fav)
root.mount("/follows", apps.follows)
root.mount("/timeline", apps.timeline)
root.mount("/user", apps.user)
JWT_SALT = random_str()

for app in (apps.auth, apps.fav, apps.follows, apps.timeline, apps.user):
    app.install(SQLitePlugin(dbfile='honk.db'))
    app.install(JwtPlugin(validation, JWT_SALT))
    set_err_handler(app)
