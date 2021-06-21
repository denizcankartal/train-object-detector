## Introduction
- This docker image has been created to easily train object detection models using the __[TensorFlow Object Detection API](https://github.com/tensorflow/models/blob/master/research/object_detection/README.md)__.
- Before issuing any of the commands down below, make sure you have docker installed.
- To install and learn about docker visit __[here](https://www.docker.com/get-started)__
- Once you installed docker, build and run the container by using the commands below.
- This docker image has everything that is necessary to train a custom object detector, therefore you do not need to install any dependencies or packages in your local machine.
- All the steps required to train a model are explained and issued in a python notebook, "training_guide.ipynb". So simply read the markdowns and execute the cells.
- That python notebook also provides references and resources for further research and development.

## Build the docker image
<pre>
docker build -t train-object-detector
</pre>

## Run the docker container
<pre>
docker run -it -p [LOCAL_PORT]:[CONTAINER_PORT] -p [LOCAL_PORT]:[CONTAINER_PORT] -v [PATH_TO_IMAGE_FOLDER]/train-object-detector:/home/workspace train-object-detector
</pre>

## Run jupyter notebook inside the container
<pre>
jupyter notebook --port=[PORT] --no-browser --ip=0.0.0.0 --allow-root
</pre>

## Connecting to a running Docker container 
<pre>
# list all runnning containers
docker ps
# get the container ID by inspecting the output of "docker ps", and connect to that container
docker exec -i -t [CONTAINER_ID] bash
</pre>

## Send a video stream into the container
<pre>
docker run -it --device=[VIDEO_PATH]
</pre>
