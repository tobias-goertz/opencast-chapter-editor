from flask import request
from app import app
from .service.settings_service import get_settings
from .service.segments_service import get_segments, publish_segments
from .service.response_service import error
from .service.video_service import get_video, get_video_list


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
    return get_video_list()


# returns Video sources in array of types in orderd resolution
@app.route('/media')
def search():
    id = request.args.get('id')
    if id:
        result = get_video(id)
        return result.message
    else:
        return error("No ID provided", 422)


# publishes segments based on type (save or publish) via segments_service
@app.route('/upload', methods=['POST'])
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
