from flask import request, make_response, jsonify
from backend import app, session
import json
import xmltodict
from natsort import natsorted
from os import environ
from datetime import datetime


opencast_url = environ.get('OPENCAST_URL')


@app.route('/settings')
def settings():
    # deactivated until /chapter-editor/settings.json is available
    # res = session.get(
    #       f'{opencast_url}/ui/config/studio/settings.json',
    #       auth=('admin', 'opencast'))
    # if res.status_code != 200:
    #     return error(res.text, res.status_code)
    # else:
    #     return res.json()
    with open('ui-settings-sample.json') as json_file:
        data = json.load(json_file)
    return data


@app.route('/segmentsOld')
def segmentsOld():
    id = request.args.get('id')
    if id:
        r = session.get(
            f'{opencast_url}/search/episode.json?id={id}',
            auth=('admin', 'opencast')).json()
        if 'segments' in r['search-results']['result']:
            duration = r['search-results']['result']['mediapackage']['duration']
            segments = r['search-results']['result']['segments']['segment']
            payload = {'duration': duration, 'segments' : segments}
            return payload
        else:
            return error("No Segments found", 404)
    else:
        return error("No ID provided", 422)


@app.route('/segments')
def segments():
    id = request.args.get('id')
    if id:
        catalogs = session.get(
            f'{opencast_url}/admin-ng/event/{id}/asset/catalog/catalogs.json',
            auth=('admin', 'opencast')).json()
        for catalog in catalogs:
            if catalog['type'] == 'mpeg-7/segments':
                assetUrl = catalog['url']
        segmentsXml = session.get(assetUrl, auth=('admin', 'opencast')).text
        parsedSegmentsXml = xmltodict.parse(segmentsXml)
        segments = parsedSegmentsXml['Mpeg7']['Description']['MultimediaContent']['Video']['TemporalDecomposition']['VideoSegment']
        convertedSegments = []
        for segment in segments:
            convertedSegment = {}
            convertedSegment['time'] = FromMediaRelTimePoint(segment['MediaTime']['MediaRelTimePoint'])
            convertedSegment['duration'] = FromMediaDuration(segment['MediaTime']['MediaDuration'])
            convertedSegments.append(convertedSegment)
        payload = {'segments': convertedSegments}
        return payload
    else:
        return error("No ID provided", 422)


@app.route('/videos')
def videos():
    res = session.get(
               f'{opencast_url}/api/events',
               auth=('admin', 'opencast')).json()
    payload = {'videos': res, 'opencastUrl': opencast_url}
    return json.dumps(payload)


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


@app.route('/publish', methods=['POST'])
def publish():
    id = request.args.get('id')
    type = request.args.get('type')

    if id and type:
        if len(request.json['segments']) > 0:
            segments = request.json['segments']
            with open('backend/base.xml') as base:
                data = xmltodict.parse(base.read())
            videoSegments = []
            for index, segment in enumerate(segments, start=1):
                seg = {}
                seg["@id"] = f'segment-{index}'
                seg['MediaTime'] = {
                    "MediaRelTimePoint": ToMediaRelTimePoint(segment['time']),
                    "MediaDuration": ToMediaDuration(segment['duration'])
                }
                videoSegments.append(seg)
            data['Mpeg7']['Description']['MultimediaContent']['Video']['TemporalDecomposition']['VideoSegment'] = videoSegments
            parsedXml = xmltodict.unparse(data)
            url = f'{opencast_url}/admin-ng/event/{id}/assets'
            file = {'catalog_segments_xml.0': ('segments.xml', parsedXml, 'text/xml')}
            req = session.post(url, data=segmentsPayload(type),
                               files=file, auth=('admin', 'opencast'))
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
    postData = config['postData']
    if type == 'save':
        postData['processing']['workflow'] = config['saveWorkflowID']
    elif type == 'publish':
        postData['processing']['workflow'] = config['publishWorkflowID']
    return {'metadata': json.dumps(postData)}


def error(message, status_code):
    return make_response(jsonify(message), status_code)
