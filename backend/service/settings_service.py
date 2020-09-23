from backend import session, opencast_url
from .response_service import error


def get_settings():
    # in case /chapter-editor/settings.json is not available:
    # with open('ui-settings-sample.json') as json_file:
    #     data = json.load(json_file)
    # return data
    res = session.get(
          f'{opencast_url}/ui/config/chapter-editor/settings.json')
    if res.status_code != 200:
        return error(res.text, res.status_code)
    else:
        return res.json()
