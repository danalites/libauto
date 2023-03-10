FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y python3 ffmpeg python3-pip


ADD . /app/
WORKDIR /app
RUN pip install -r requirements.txt

ENTRYPOINT [ "python3" ]
CMD ["server.py" ]