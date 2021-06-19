import json
from bottle import HTTP_CODES, Bottle, HTTPError, response

def err_4xx(error):
    response.content_type = "application/json"
    return json.dumps({"status": error.body})

def err_500(error: HTTPError):
    response.content_type = "application/json"
    if isinstance(error.exception, KeyError):
        response.status = 400
        return json.dumps({"status": "Missing fields"})
    return json.dumps({"status": "Internal server error"})

def set_err_handler(app: Bottle):
    app.error_handler[500] = err_500
    for code in HTTP_CODES.keys():
        if code >= 400 and code < 500:
            app.error_handler[code] = err_4xx
