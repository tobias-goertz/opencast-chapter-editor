from flask import Flask
from config import Config
from flask_cors import CORS
import requests
from os import environ
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
session.auth = (environ.get('OPENCAST_USER'), environ.get('OPENCAST_PW'))
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
opencast_url = environ.get('OPENCAST_URL')


app = Flask(__name__)
app.config.from_object(Config)

CORS(app, resources={r'/*': {'origins': '*'}})

if __name__ == "__main__":
    app.run()

from backend import routes
