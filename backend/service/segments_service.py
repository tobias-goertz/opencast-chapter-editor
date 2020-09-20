from backend import session, opencast_url
import json
from .response_service import error, success
from .mpeg_7_service import mpeg7_to_dict, dict_to_mpeg7
from .settings_service import get_settings


def get_segments(id):
    callback = get_segments_xml(id)
    if callback.get('status_code') == 400:
        return get_public_segments(id)
    else:
        return callback.get('message')


def get_segments_xml(id):
    res = session.get(f'{opencast_url}/assets/episode/{id}')
    if res.status_code == 200:
        return mpeg7_to_dict(res)
    else:
        return error("mediapackage not found", 404)


def get_public_segments(id):
    res = session.get(
        f'{opencast_url}/search/episode.json?id={id}').json()
    try:
        duration = res['search-results']['result']['mediapackage']['duration'] / 1000
        segments = res['search-results']['result']['segments']['segment']
        for segment in segments:
            segment['duration'] = segment.get('duration') / 1000
            segment['time'] = segment.get('time') / 1000
            for key in ['relevance', 'hit', 'previews']:
                segment.pop(key)
            index = segment.get('index')
            segment['title'] = f'segment-{index}'
        payload = dict(duration=duration, segments=segments, type='public')
        return success(payload, 200)
    except KeyError:
        return error("No published segments found", 404)


def publish_segments(id, type, video_url, video_duration, segments):
    mpeg_7 = dict_to_mpeg7(segments, video_url, video_duration)
    url = f'{opencast_url}/admin-ng/event/{id}/assets'
    file = {'catalog_segments_xml.0': ('segments.xml', mpeg_7, 'text/xml')}
    req = session.post(url, data=segmentsPayload(type), files=file)
    if req.status_code != 201:
        return error(req.text, req.status_code)
    else:
        return req.text


def segmentsPayload(type):
    config = get_settings()['upload']
    post_data = config['postData']
    if type == 'save':
        post_data['processing']['workflow'] = config['saveWorkflowID']
    elif type == 'publish':
        post_data['processing']['workflow'] = config['publishWorkflowID']
    return {'metadata': json.dumps(post_data)}
