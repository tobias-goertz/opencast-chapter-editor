from flask import request
from backend import app, session, opencast_url
import json
import xmltodict
from natsort import natsorted
from os import environ
from .service.settings_service import get_settings
from .service.segments_service import get_segments, publish_segments
from .service.response_service import error


# returns settings from oc-config via settings_service
@app.route('/settings')
def settings():
    return get_settings()


# returns segments via segments_service
@app.route('/segments')
def segments():
    id = request.args.get('id')
    if id:
        return get_segments(id)
    else:
        return error("No ID provided", 400)


# video index for dev and testing only
@app.route('/videos')
def videos():
    res = session.get(
               f'{opencast_url}/api/events').json()
    payload = dict(videos=res, opencastUrl=opencast_url)
    return json.dumps(payload)


# returns event including publication (not used anymore)
@app.route('/video')
def video():
    id = request.args.get('id')
    if id:
        res = session.get(
                   f'{opencast_url}/api/events/{id}?withpublications=true',
              ).json()
        if res:
            return res
        else:
            return error("Video not found", 404)
    else:
        return error("No ID provided", 400)


# returns Video sources in array of types in orderd resolution
@app.route('/search')
def search():
    id = request.args.get('id')
    if id:
        req = session.get(
                   f'{opencast_url}/search/episode.json?id={id}').json()
        if 'result' in req['search-results']:
            mediapackage = req['search-results']['result']['mediapackage']
            tracks = mediapackage['media']['track']
            presenter = []
            presentation = []
            other = []

            if type(tracks) is dict:
                tracks = [tracks]

            for track in tracks:
                td = dict()
                td['id'] = track.get('id')
                td['type'] = track.get('type')
                td['url'] = track.get('url')
                td['duration'] = track.get('duration') / 1000
                td['resolution'] = track['video']['resolution']
                if 'presenter' in track['type']:
                    presenter.append(td)
                elif 'presentation' in track['type']:
                    presentation.append(td)
                else:
                    other.append(td)

            presenter = natsorted(
                                   presenter,
                                   key=lambda x: x.get('resolution')
                                 )
            presentation = natsorted(
                                      presentation,
                                      key=lambda x: x.get('resolution')
                                    )
            other = natsorted(other, key=lambda x: x.get('resolution'))
            title = mediapackage.get('title')
            v = dict(presenter=presenter,
                     presentation=presentation,
                     other=other,
                     title=title)
            return v
        else:
            return error("Video not found", 404)
    else:
        return error("No ID provided", 422)


# publishes segments based on type (save or publish) via segments_service
@app.route('/publish', methods=['POST'])
def publish():
    id = request.args.get('id')
    type = request.args.get('type')
    video_url = request.json.get('videoUrl')
    video_duration = request.json.get('videoDuration')
    if id and type and video_url:
        if len(request.json.get('segments')) > 0:
            segments = request.json.get('segments')
            return publish_segments(id, type, video_url, video_duration, segments)
        else:
            return error("No Segments Provided", 422)
    else:
        return error("No ID provided", 422)
