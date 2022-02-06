FROM python:3-slim
LABEL maintainer="guillaume@gauvr.it"

WORKDIR /srv/user
EXPOSE 8000

RUN pip install poetry

RUN useradd user --home /home/user && \
    mkdir -p /home/user/metrics && \
    chown -R user:user /home/user && \
    chown -R user:user /srv/user
USER user


ENV PROMETHEUS_MULTIPROC_DIR=/home/user/metrics
COPY pyproject.toml poetry.lock /srv/user/
RUN poetry install
COPY . /srv/user/
RUN poetry install

CMD ["poetry", "run", "gunicorn", "-w" , "2", "-b", "0.0.0.0:8000", "notif.wsgi"]
