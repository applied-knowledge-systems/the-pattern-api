FROM ubuntu:18.04

RUN apt-get update -y && \
    apt-get install -y git python3 python3-pip curl gnupg python3-setuptools

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN pip3 install -U pip
# RUN curl https://sh.rustup.rs -sSf | sh -s -- -y && source $HOME/.cargo/env

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

EXPOSE 8181/tcp 

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]