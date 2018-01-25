# Use an official Python runtime as a parent image
FROM nvidia/cuda:8.0-cudnn7-devel-ubuntu16.04

# Set the working directory to /OncoServe
WORKDIR /OncoText

# Copy the current directory contents into the container at /OncoServe
ADD . /OncoText

# Install any needed packages specified in requirements.txt
RUN apt-get update
RUN apt-get install --yes --force-yes software-properties-common python-software-properties
RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update
RUN apt-get --yes --force-yes install python3.6 python3.6-dev python3.6-venv wget
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3.6 get-pip.py
RUN ln -s /usr/bin/python3.6 /usr/local/bin/python3

RUN pip3 install -r requirements.txt
RUN pip3 install -r text_nn/requirements3.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000
EXPOSE 80

# Define environment variable
ENV NAME OncoText

# Run app.py when the container launches
CMD python3 /OncoText/scripts/app.py
