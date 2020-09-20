from flask import make_response, jsonify


def success(message, status_code):
    return {'message': message, 'status_code': status_code}


def error(message, status_code):
    return make_response(jsonify(message), status_code)
