#!/bin/bash

IMAGE_NAME="kinect-base"

# Check if the Docker image exists
if docker images -q "$IMAGE_NAME" > /dev/null 2>&1; then
    echo "Deleting Docker image: $IMAGE_NAME"
    docker rmi "$IMAGE_NAME"
    echo "Image deleted."
else
    echo "Docker image '$IMAGE_NAME' not found."
fi
