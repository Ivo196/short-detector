#!/bin/bash

# Check if username is provided
if [ -z "$1" ]; then
    echo "Usage: ./publish_docker.sh <dockerhub_username>"
    exit 1
fi

USERNAME=$1
IMAGE_NAME="short-detector"
PLATFORMS="linux/amd64,linux/arm64"

echo "🐳 Logging in to Docker Hub..."
docker login

echo "🛠️ Creating buildx builder..."
# Create a new builder instance or use existing
docker buildx create --use --name multi-arch-builder || docker buildx use multi-arch-builder

echo "🚀 Building and Pushing for platforms: $PLATFORMS..."
docker buildx build \
  --platform $PLATFORMS \
  --tag $USERNAME/$IMAGE_NAME:latest \
  --push \
  .

echo "✅ Done! Image $USERNAME/$IMAGE_NAME:latest pushed successfully."
