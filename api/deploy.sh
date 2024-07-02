#!/bin/bash

REPO_PATH="us-central1-docker.pkg.dev/finngpt-427606/models"

echo "Which Dockerfile do you want to build and push?"
echo "1. Dockerfile.chat"
echo "2. Dockerfile.base"
read -p "Enter your choice (1 or 2): " choice

case $choice in
    1)
        IMAGE_NAME="chat-finn-gpt"
        DOCKERFILE="Dockerfile.chat"
        ;;
    2)
        IMAGE_NAME="base-finn-gpt"
        DOCKERFILE="Dockerfile.base"
        ;;
    *)
        echo "Invalid choice. Please run the script again and select 1 or 2."
        exit 1
        ;;
esac

echo "Building $DOCKERFILE..."
docker build --platform linux/amd64 -t $REPO_PATH/$IMAGE_NAME -f $DOCKERFILE ..

if [ $? -eq 0 ]; then
    echo "Pushing $IMAGE_NAME to repository..."
    docker push $REPO_PATH/$IMAGE_NAME
    
    if [ $? -eq 0 ]; then
        echo "Successfully built and pushed $IMAGE_NAME."
    else
        echo "Failed to push $IMAGE_NAME. Please check your Docker configuration and try again."
        exit 1
    fi
else
    echo "Build failed. Skipping push step."
    exit 1
fi

echo "Build and push process completed."