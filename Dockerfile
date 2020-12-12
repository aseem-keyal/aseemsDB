FROM ubuntu:21.04

ENV DEBIAN_FRONTEND="noninteractive" TZ="America/New_York"
RUN apt-get update && apt-get install -y \
	python3-pip \
	python3-recoll \
	poppler-utils

RUN pip3 install --no-cache-dir uvicorn gunicorn fastapi jinja2 aiofiles uvloop httptools websockets

COPY ./start.sh /start.sh
RUN chmod +x /start.sh

COPY ./gunicorn_conf.py /gunicorn_conf.py
COPY ./recoll.conf /root/.recoll/recoll.conf


COPY ./app /app
RUN mkdir /app/static/packet_archive
VOLUME /app/static/packet_archive
WORKDIR /app/

ENV PYTHONPATH=/app

EXPOSE 80

CMD ["/start.sh"]
