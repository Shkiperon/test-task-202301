FROM python:3.10.6-slim-bullseye

WORKDIR /app

COPY --chown=www-data:www-data /app/requirements.txt /app/requirements.txt

RUN cp /usr/share/zoneinfo/Asia/Yekaterinburg /etc/localtime \
    && apt update \
    && apt install -y build-essential python3-dev uwsgi-plugin-python3 \
    && pip3 install -U pip \
    && pip3 install uwsgi \
    && pip3 install -r /app/requirements.txt \
    && pip3 cache purge \
    && apt remove -y build-essential python3-dev \
    && apt clean && rm -rf /var/cache/apt/archives/*

COPY --chown=www-data:www-data /app /app

USER www-data
ENV PYTHONUNBUFFERED=1
EXPOSE 5000
CMD ["uwsgi", "--master", "--workers=2", "--threads=2", "--logformat=%(addr) (%(user)) (%(vars) vars in %(pktsize) bytes) (%(ctime)) %(method) %(uri) => generated %(rsize) bytes in %(msecs) msecs (%(proto) %(status)) %(headers) headers in %(hsize) bytes (%(switches) switches on core %(core))","--http=0.0.0.0:5000", "--wsgi-file=/app/run.py" ]
