# Opencast Chapter-Editor
Bachelor Thesis Project: Development of a web-based Chapter Editor for Lecture Recordings in [Opencast](https://opencast.org)

## Project Setup
This Project uses Flask as Backend and Vue.js as Frontend.
The Backend can be served with docker, the frontend is a static SPA build with yarn and need to be served with a web server.

### All-in-one
To kickstart use the `docker-compose.nginx.yml` docker script wich starts backend and frontend with NGINX:
```
docker-compose -f docker-compose.nginx.yml up
```
Now you can launch the application on [`http://localhost`](http://localhost).

If you want to install the app on a server, depending one the way of serving, a seperate start of backend and frontend might be recommended. More about configuration for production see [configuration](#configuration) section.
### Backend
Start the backend Server with docker-compose script:
```
docker-compose up --build -d
```
You need to configure the `docker-compose.yml` to connect the backend with your opencast instance:
```
- OPENCAST_URL=https://develop.opencast.org
- OPENCAST_USER=admin
- OPENCAST_PW=opencast
```
It's recommended to add a new user for the chapter-editor in opencast with admin rights, see [API](#opencast-apis-used-by-chapter-editor) section below.

### Frontend

You need to configure some enviroment variables to work.
Edit the created `.env` for your purposes. For production builds with NGINX, see [configuration](#configure) chapter below.

```
cd frontend
cp .env.sample .env.production
```

To build the Chapter-Editor yourself [install yarn](https://classic.yarnpkg.com/en/docs/install) and execute these commands:

```
cd frontend
yarn install
yarn build
```

This will generate static content you can serve via any web server in `dist/`.
That's it.

## Opencast APIs used by Chapter-Editor
Opencast Studio uses the following APIs:

- `/search`
- `/assets/episode`
- `/admin-ng/event`
- `ui/config/`

You have to make sure that these APIs are accessible to the user using Chapter-Editor. A Role `ROLE_CHAPTER_EDITOR` should be created in the security configuration (e.g. `mh_default_org.xml`) of Opencast.

## Configuration
To work with opencast, you can specify some configuration options for opencast: [`ui-settings.md`](docs/ui-settings.md).

#### NGINX configuration
To run the Chapter-Editor on a server, you can use NGINX to serve the generated static `dist/` content and reverse proxy the backend-docker-container. An Example NGINX configuration for that can be found here: [`nginx.conf`](/docs/nginx.conf).
If you reverse proxy the backend-container, you need to specify the `VUE_APP_BACKEND_PROXY_PASS_LOCATION` enviroment variable in the `.env.production` for the frontend. E.g. if `/api/` is the location, you need to set `/api` as value and remove the `VUE_APP_BACKEND_URL` since it got proxied by the same URL.

## Development

### Backend
For local development install [pipenv](https://pypi.org/project/pipenv/) and Python 3.8.6. Create a virtual  enviroment with pipenv, activate it and start Flask:
```
cd backend
pipenv install
pipenv shell
flask run
```

### Frontend
If you prefer to run a local development server directly, you can use this
instead:

```
cd frontend
yarn serve
```
