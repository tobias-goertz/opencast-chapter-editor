from flask import make_response, jsonify
from types import SimpleNamespace


def success(message, status_code):
    result = {'message': message, 'status_code': status_code}
    return SimpleNamespace(**result)


def error(message, status_code):
    return make_response(jsonify(message), status_code)
