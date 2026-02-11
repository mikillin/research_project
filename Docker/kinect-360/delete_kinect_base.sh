#!/bin/bash

IMAGE_NAME="kinect-base"

echo "Stopping and removing containers using image: $IMAGE_NAME"

# Find all container IDs using given image (running or stopped)
CONTAINERS=$(docker ps -a -q --filter ancestor="$IMAGE_NAME")

if [ -z "$CONTAINERS" ]; then
  echo "No containers found for image $IMAGE_NAME."
else
  # Stop running containers
  RUNNING_CONTAINERS=$(docker ps -q --filter ancestor="$IMAGE_NAME")
  if [ -n "$RUNNING_CONTAINERS" ]; then
    echo "Stopping running containers..."
    docker stop $RUNNING_CONTAINERS
  fi

  echo "Removing containers..."
  docker rm $CONTAINERS
fi

echo "Deleting image: $IMAGE_NAME"

docker rmi "$IMAGE_NAME"