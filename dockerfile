FROM ubuntu:14.04
MAINTAINER Your Name "yourname@mit.edu"
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN apt-get install -y curl vim
RUN pip install flask
COPY . /app
WORKDIR /app
RUN export FLASK_APP=classifierAPI.py; export FLASK_DEBUG=1
ENTRYPOINT ["python"]
CMD ["classifierAPI.py"]`
