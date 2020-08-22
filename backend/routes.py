from flask import request, make_response, jsonify
from backend import app, session
import json
import xmltodict
from natsort import natsorted
from os import environ
from datetime import datetime

opencast_url = environ.get('OPENCAST_URL')


@app.route('/segments')
def segments():
    id = request.args.get('id')
    if id:
        r = session.get(
            f'{opencast_url}/search/episode.json?id={id}',
            auth=('admin', 'opencast')).json()
        if 'segments' in r['search-results']['result']:
            return r['search-results']['result']['segments']
        else:
            return error("No Segments found", 404)
    else:
        return error("No ID provided", 422)


@app.route('/videos')
def videos():
    res = session.get(
               f'{opencast_url}/admin-ng/event/events.json',
               auth=('admin', 'opencast')).json()
    return res

@app.route('/video')
def video():
    id = request.args.get('id')
    if id:
        res = session.get(
                   f'{opencast_url}/api/events/{id}?withpublications=true',
                   auth=('admin', 'opencast')).json()
        if res:
            return res
        else:
            return error("Video not found", 404)
    else:
        return error("No ID provided", 422)

