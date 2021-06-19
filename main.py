from bottle import Bottle, BaseRequest, response, error
from bottle_sqlite import SQLitePlugin
from bottlejwt import JwtPlugin

import apps

from utils import random_str, set_err_handler

root = Bottle()
def validation(auth, auth_value):
    return True
root.mount("/auth", apps.auth)
root.mount("/follows", apps.follows)
root.mount("/timeline", apps.timeline)
root.mount("/user", apps.user)
jwt_salt = "test"

for app in (apps.auth, apps.follows, apps.timeline, apps.user):
    app.install(SQLitePlugin(dbfile='honk.db'))
    app.install(JwtPlugin(validation, jwt_salt))
    set_err_handler(app)


root.run(host="localhost", port=8080, debug=True, reloader=True)