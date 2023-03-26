VERSION 0.7
FROM ubuntu:18.04

deps:
    FROM ../dependencies+common-build-deps
    WORKDIR /app
    RUN apt-get update && apt-get install -yqq --no-install-recommends python3 python3-pip python3-setuptools python3-dev 
    RUN pip3 install wheel
    COPY requirements.txt ./
    RUN pip3 wheel -r requirements.txt --wheel-dir=wheels

build:
    FROM +deps
    WORKDIR /app
    COPY . /app
    SAVE ARTIFACT /app /app

docker:
    FROM +deps
    WORKDIR /app
    COPY +build/app /app
    RUN pip3 install --no-index --find-links=wheels -r requirements.txt
    EXPOSE 8181/tcp 
    ENTRYPOINT [ "python3","app.py"]
    SAVE IMAGE --push ghcr.io/applied-knowledge-systems/the-pattern-api:latest