# ubuntu base image
FROM ubuntu:20.04

# configuring tzdata issue
ARG DEBIAN_FRONTEND=noninteractive

# copy everything from current working directory at local host to /app in docker image
# COPY source dest, e.g. COPY . /home
COPY . /home/workspace

WORKDIR /home

# update system before installing packages
RUN apt-get update

##### INSTALL SYSTEM DEPENDENCIES AND PACKAGES #######
RUN apt-get install -y \
    python3-pip \
    python3.8 \
    wget \
    nano \
    unzip \
    curl \
    git \
    g++ \
    cmake \
    protobuf-compiler \
    python-pil \
    python-lxml

##### INSTALL TensorFlow 2.5.0
RUN pip3 install tensorflow==2.5.0

##### INSTALL jupyter
RUN pip3 install jupyter

##### DOWNLOAD AND BUILD PROTOBUF ######
ENV PROTOC_VERSION=v3.17.3
ENV PROTOC_ZIP=protoc-3.17.3-linux-x86_64.zip

RUN wget https://github.com/protocolbuffers/protobuf/releases/download/${PROTOC_VERSION}/${PROTOC_ZIP} \
	&& unzip -o ${PROTOC_ZIP} -d ./proto \
	&& rm -r ${PROTOC_ZIP} \
	&& chmod 755 -R ./proto/bin \
	&& BASE=/usr \
	&& cp ./proto/bin/protoc ${BASE}/bin/ \
	&& cp -R ./proto/include/* ${BASE}/include/

###### DOWNLOAD TENSORFLOW MODELS ######
RUN cd /home \
    && wget https://github.com/tensorflow/models/archive/master.zip \
 	&& unzip master.zip \
	&& rm -r master.zip \
	&& mv ./models-master ./models \
	&& cd models/research/ \
	&& protoc object_detection/protos/*.proto --python_out=. \
    && cp object_detection/packages/tf2/setup.py . \
    && python3 -m pip install . \
	&& cd /home

####### SELENIUM SETUP FOR "image_downloader.py" ##############
# selenium requires a driver to interface with the chosen
# browser, firefox requires geckodriver.

# 1. install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# 2. install chromedriver
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# which chromedriver
RUN pip3 install \
    pandas \
    prompt_toolkit \
    regex \
    selenium \
    beautifulsoup4