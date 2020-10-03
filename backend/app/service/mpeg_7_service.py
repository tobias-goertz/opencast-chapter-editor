from app import session
from datetime import datetime
from .response_service import error, success
import xmltodict


def mpeg7_to_dict(res):
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
        return error("no segments.xml available", 400)

    segments_xml = session.get(asset_url).text
    parsed_segments_xml = xmltodict.parse(segments_xml)
    segments = parsed_segments_xml['Mpeg7']['Description']['MultimediaContent']['Video']['TemporalDecomposition']['VideoSegment']
    converted_duration = FromMediaDuration(parsed_segments_xml['Mpeg7']['Description']['MultimediaContent']['Video']['MediaTime']['MediaDuration'])
    converted_segments = []
    if type(segments) is list:
        for segment in segments:
            time = FromMediaRelTimePoint(segment['MediaTime']['MediaRelTimePoint'])
            duration = FromMediaDuration(segment['MediaTime']['MediaDuration'])
            if 'MediaTitle' in segment:
                title = segment['MediaTitle']
            else:
                title = segment['@id']
            converted_segment = dict(time=time, duration=duration, title=title)
            converted_segments.append(converted_segment)
        result = dict(segments=converted_segments, duration=converted_duration)
        return success(result, 200)
    else:
        return error("No segments found", 400)


def dict_to_mpeg7(segments, video_url, video_duration):
    with open('backend/base.xml') as base:
        data = xmltodict.parse(base.read())
    video_segments = []
    for index, segment in enumerate(segments, start=0):
        seg = dict()
        seg['@id'] = f'segment-{index}'
        seg['MediaTitle'] = segment.get('title')
        seg['MediaTime'] = {
            'MediaRelTimePoint': ToMediaRelTimePoint(segment['time']),
            'MediaDuration': ToMediaDuration(segment['duration'])
        }
        video_segments.append(seg)
    video = data['Mpeg7']['Description']['MultimediaContent']['Video']
    video['TemporalDecomposition']['VideoSegment'] = video_segments
    video['MediaLocator']['MediaUri'] = video_url
    video['MediaTime']['MediaDuration'] = ToMediaDuration(video_duration)
    parsed_xml = xmltodict.unparse(data)
    return parsed_xml


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


def ToMediaRelTimePoint(t):
    time = datetime.utcfromtimestamp(t).strftime('%H:%M:%S:%f')[:-4]
    return f'T{time}F1000'


def ToMediaDuration(d):
    time = datetime.utcfromtimestamp(d).strftime('PT%MM%SS%f')[:-4]
    return f'{time}N1000F'
