from flask import request, make_response, jsonify
from backend import app, session
import json
import xmltodict
from natsort import natsorted
from os import environ
from datetime import datetime


opencast_url = environ.get('OPENCAST_URL')
opencast_auth = (environ.get('OPENCAST_USER'), environ.get('OPENCAST_PW'))


@app.route('/settings')
def settings():
    # deactivated until /chapter-editor/settings.json is available
    # res = session.get(
    #       f'{opencast_url}/ui/config/studio/settings.json',
    #       auth=opencast_auth)
    # if res.status_code != 200:
    #     return error(res.text, res.status_code)
    # else:
    #     return res.json()
    with open('ui-settings-sample.json') as json_file:
        data = json.load(json_file)
    return data


@app.route('/segments')
def segments():
    id = request.args.get('id')
    if id:
        res = session.get(
            f'{opencast_url}/assets/episode/{id}',
            auth=opencast_auth)
        if res.status_code == 200:
            parsed_mediapackage = xmltodict.parse(res.text)
            catalogs = parsed_mediapackage['mediapackage']['metadata']['catalog']
            if type(catalogs) is list:
                for catalog in catalogs:
                    if catalog.get('@type') == 'mpeg-7/segments':
                        asset_url = catalog['url']
            else:
                if catalogs.get('@type') == 'mpeg-7/segments':
                    asset_url = catalogs['url']
            try:
                asset_url
            except NameError:
                return public_segments(id)

            segments_xml = session.get(asset_url, auth=opencast_auth).text
            parsed_segments_xml = xmltodict.parse(segments_xml)
            segments = parsed_segments_xml['Mpeg7']['Description']['MultimediaContent']['Video']['TemporalDecomposition']['VideoSegment']
            converted_duration = FromMediaDuration(parsed_segments_xml['Mpeg7']['Description']['MultimediaContent']['Video']['MediaTime']['MediaDuration'])
            converted_segments = []
            if type(segments) is list:
                for segment in segments:
                    time = FromMediaRelTimePoint(segment['MediaTime']['MediaRelTimePoint'])
                    duration = FromMediaDuration(segment['MediaTime']['MediaDuration'])
                    title = segment['@id']
                    converted_segment = dict(time=time, duration=duration, title=title)
                    converted_segments.append(converted_segment)
                payload = dict(segments=converted_segments, duration=converted_duration)
                return payload
            else:
                return error("No segments found", 404)
        else:
            return error("mediapackage not found", 404)
    else:
        return error("No ID provided", 400)


def public_segments(id):
    res = session.get(
        f'{opencast_url}/search/episode.json?id={id}',
        auth=opencast_auth).json()
    try:
        duration = res['search-results']['result']['mediapackage']['duration']
        segments = res['search-results']['result']['segments']['segment']
        for segment in segments:
            segment['duration'] = segment.get('duration') / 1000
            segment['time'] = segment.get('time') / 1000
            for key in ['relevance', 'hit', 'previews']:
                segment.pop(key)
            index = segment.get('index')
            segment['title'] = f'segment-{index}'
        payload = dict(duration=duration, segments=segments, type='public')
        return payload
    except KeyError:
        return error("No published segments found", 404)


@app.route('/videos')
def videos():
    res = session.get(
               f'{opencast_url}/api/events',
               auth=opencast_auth).json()
    payload = dict(videos=res, opencastUrl=opencast_url)
    return json.dumps(payload)


@app.route('/video')
def video():
    id = request.args.get('id')
    if id:
        res = session.get(
                   f'{opencast_url}/api/events/{id}?withpublications=true',
                   auth=opencast_auth).json()
        if res:
            return res
        else:
            return error("Video not found", 404)
    else:
        return error("No ID provided", 400)


@app.route('/search')
def search():
    id = request.args.get('id')
    if id:
        req = session.get(
                   f'{opencast_url}/search/episode.json?id={id}',
                   auth=opencast_auth).json()
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


@app.route('/publish', methods=['POST'])
def publish():
    id = request.args.get('id')
    type = request.args.get('type')
    video_url = request.json.get('videoUrl')
    video_duration = request.json.get('videoDuration')
    if id and type and video_url:
        if len(request.json.get('segments')) > 0:
            segments = request.json.get('segments')
            with open('backend/base.xml') as base:
                data = xmltodict.parse(base.read())
            video_segments = []
            for index, segment in enumerate(segments, start=1):
                seg = dict()
                seg["@id"] = segment.get('title')
                seg['MediaTime'] = {
                    "MediaRelTimePoint": ToMediaRelTimePoint(segment['time']),
                    "MediaDuration": ToMediaDuration(segment['duration'])
                }
                video_segments.append(seg)
            video = data['Mpeg7']['Description']['MultimediaContent']['Video']
            video['TemporalDecomposition']['VideoSegment'] = video_segments
            video['MediaLocator']['MediaUri'] = video_url
            video['MediaTime']['MediaDuration'] = ToMediaDuration(video_duration)
            parsed_xml = xmltodict.unparse(data)
            url = f'{opencast_url}/admin-ng/event/{id}/assets'
            file = {'catalog_segments_xml.0': ('segments.xml', parsed_xml, 'text/xml')}
            req = session.post(url, data=segmentsPayload(type),
                               files=file, auth=opencast_auth)
            if req.status_code != 201:
                return error(req.text, req.status_code)
            else:
                return req.text
        else:
            return error("No Segments Provided", 422)
    else:
        return error("No ID provided", 422)


def ToMediaRelTimePoint(t):
    time = datetime.utcfromtimestamp(t).strftime('%H:%M:%S:%f')[:-4]
    return f'T{time}F1000'


def ToMediaDuration(d):
    time = datetime.utcfromtimestamp(d).strftime('PT%MM%SS%f')[:-4]
    return f'{time}N1000F'


def FromMediaRelTimePoint(t):
    time = t.replace('F1000', '')
    time = datetime.strptime(time, 'T%H:%M:%S:%f')
    time_seconds = time.second + time.minute*60 + time.hour*3600
    return time_seconds


def FromMediaDuration(duration):
    duration = duration.replace('N1000F', '')
    duration = datetime.strptime(duration, 'PT%MM%SS%f')
    duration_seconds = duration.second + duration.minute*60 + duration.hour*3600
    return duration_seconds


def segmentsPayload(type):
    config = settings()['upload']
    post_data = config['postData']
    if type == 'save':
        post_data['processing']['workflow'] = config['saveWorkflowID']
    elif type == 'publish':
        post_data['processing']['workflow'] = config['publishWorkflowID']
    return {'metadata': json.dumps(post_data)}


def error(message, status_code):
    return make_response(jsonify(message), status_code)
