FROM python:3.7-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apk add --no-cache --virtual .build-deps gcc musl-dev \
 && pip install --no-cache-dir -r requirements.txt \
 && apk del .build-deps

COPY run.py ./run.py
COPY job.json ./job.json
COPY configs ./configs

ENTRYPOINT ["dumb-init", "--"]

CMD ["python", "./run.py"]
