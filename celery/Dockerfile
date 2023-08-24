FROM python:3.11.2

WORKDIR /flaskblog

COPY requirements.txt /flaskblog/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /flaskblog/

ENV C_FORCE_ROOT="true"

CMD ["celery", "-A", "run.celery", "worker", "--pool=solo", "--loglevel=info"]