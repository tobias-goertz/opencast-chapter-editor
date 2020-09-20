import json


def get_settings():
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
