FROM python:alpine3.12
RUN apk add --no-cache --virtual .build-deps build-base linux-headers jpeg-dev zlib-dev
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT [ "python","depix.py" ]