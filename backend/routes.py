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


@app.route('/search')
def search():
    id = request.args.get('id')
    if id:
        req = session.get(
                   f'{opencast_url}/search/episode.json?id={id}',
                   auth=('admin', 'opencast')).json()
        if 'result' in req['search-results']:
            mediapackage = req['search-results']['result']['mediapackage']
            tracks = mediapackage['media']['track']
            v = {}
            presenter = []
            presentation = []
            other = []

            if type(tracks) is dict:
                tracks = [tracks]

            for track in tracks:
                td = {}
                td['id'] = track['id']
                td['type'] = track['type']
                td['url'] = track['url']
                td['duration'] = track['duration'] / 1000
                td['resolution'] = track['video']['resolution']
                if 'presenter' in track['type']:
                    presenter.append(td)
                elif 'presentation' in track['type']:
                    presentation.append(td)
                else:
                    other.append(td)

            v['presenter'] = natsorted(
                                        presenter,
                                        key=lambda x: x['resolution']
                                      )
            v['presentation'] = natsorted(
                                        presentation,
                                        key=lambda x: x['resolution']
                                      )
            v['other'] = natsorted(other, key=lambda x: x['resolution'])
            v['title'] = mediapackage['title']
            return v
        else:
            return error("Video not found", 404)
    else:
        return error("No ID provided", 422)

def error(message, status_code):
    return make_response(jsonify(message), status_code)
