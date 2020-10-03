from app import session, opencast_url
from .response_service import error, success
from natsort import natsorted
import json


def get_video(id):
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
        return success(v, 200)
    else:
        return error("Video not found", 404)


def get_video_list():
    res = session.get(
               f'{opencast_url}/api/events').json()
    payload = dict(videos=res, opencastUrl=opencast_url)
    return json.dumps(payload)
