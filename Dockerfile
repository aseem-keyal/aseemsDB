FROM ubuntu:20.04

ENV DEBIAN_FRONTEND="noninteractive" TZ="America/New_York"
RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository ppa:recoll-backports/recoll-1.15-on && apt-get update

RUN apt-get install -y \
	python3-pip \
	python3-recoll=1.32.7-1~ppa3~focal1 \
	poppler-utils

RUN pip3 install --no-cache-dir uvicorn gunicorn fastapi jinja2 aiofiles uvloop httptools websockets

COPY ./start.sh /start.sh
RUN chmod +x /start.sh

COPY ./start-reload.sh /start-reload.sh
RUN chmod +x /start-reload.sh

VOLUME /root/.recoll/
COPY ./gunicorn_conf.py /gunicorn_conf.py
COPY ./recoll.conf /recoll.conf

COPY ./app /app
RUN mkdir /app/static/packet_archive
VOLUME /app/static/packet_archive
WORKDIR /app/

ENV PYTHONPATH=/app

EXPOSE 80

CMD ["/start.sh"]
