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


@app.route('/publish', methods=['POST'])
def publish():
    id = request.args.get('id')
    if id:
        if len(request.json['segments']) > 0:
            segments = request.json['segments']
            with open('app/base.xml') as base:
                data = xmltodict.parse(base.read())
            videoSegments = []
            for index, segment in enumerate(segments, start=1):
                seg = {}
                seg["@id"] = f'segment-{index}'
                seg['MediaTime'] = {
                    "MediaRelTimePoint": MediaRelTimePoint(segment['time']),
                    "MediaDuration": MediaDuration(segment['duration'])
                }
                videoSegments.append(seg)
            data['Mpeg7']['Description']['MultimediaContent']['Video']['TemporalDecomposition']['VideoSegment'] = videoSegments
            parsedXml = xmltodict.unparse(data)
            url = f'{opencast_url}/admin-ng/event/{id}/assets'
            file = {'catalog_segments_xml.0': ('segments.xml', parsedXml, 'text/xml')}
            req = session.post(url, data=payload,
                                files=file, auth=('admin', 'opencast'))
            if req.status_code != 201:
                return error(req.text, req.status_code)
            else:
                return req.text
        else:
            return error("No Segments Provided", 422)
    else:
        return error("No ID provided", 422)


def MediaRelTimePoint(t):
    time = datetime.utcfromtimestamp(t).strftime('%H:%M:%S:%f')[:-4]
    return f'T{time}F1000'


def MediaDuration(d):
    time = datetime.utcfromtimestamp(d).strftime('PT%MM%SS%f')[:-4]
    return f'{time}N1000F'


postData = {
    'assets': {
        "options": [{
          "id": "catalog_segments_xml",
          "type": "catalog",
          "flavorType": "mpeg-7",
          "flavorSubType": "segments",
          "displayOrder": 3,
          "accept": ".xml",
          "title": "FOO"
        }]
    },
    "processing": {
        "workflow": "publish-uploaded-segments",
        "configuration": {
            "uploadedSearchPreview": "true",
            "downloadSourceflavorsExist": "true",
            "download-source-flavors": "mpeg-7/segments"
        }
    }
}
payload = {'metadata': json.dumps(postData)}


def error(message, status_code):
    return make_response(jsonify(message), status_code)
