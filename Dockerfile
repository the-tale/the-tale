FROM python:2.7

ENV REPO /repo
ENV PYTHONPATH ${REPO}

WORKDIR ${REPO}

RUN apt-get update && \
  apt-get -y install libmemcached-dev && \
  mkdir ~/logs && \
  mkdir ~/.the-tale

COPY . ${REPO}

RUN pip install -r requirements.txt

CMD ./manage.py runserver 0.0.0.0:8000
