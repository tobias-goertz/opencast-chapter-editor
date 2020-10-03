FROM python:3.8-alpine
WORKDIR /backend
RUN pip install pipenv
COPY Pipfile* /tmp/

ENV FLASK_APP=app
ENV FLASK_RUN_HOST=0.0.0.0

RUN cd /tmp && pipenv lock --requirements > requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY . /backend

CMD ["flask", "run"]
