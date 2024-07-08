#!/bin/bash

REPO_PATH="us-central1-docker.pkg.dev/finngpt-427606/models"

echo "Which Dockerfile(s) do you want to build and push?"
echo "1. Dockerfile.chat"
echo "2. Dockerfile.base"
echo "3. Both Dockerfile.chat and Dockerfile.base"
read -p "Enter your choice (1, 2, or 3): " choice

build_and_push() {
    local image_name=$1
    local dockerfile=$2

    echo "Building $dockerfile..."
    docker build --platform linux/amd64 -t $REPO_PATH/$image_name -f $dockerfile ..

    if [ $? -eq 0 ]; then
        echo "Pushing $image_name to repository..."
        docker push $REPO_PATH/$image_name
        
        if [ $? -eq 0 ]; then
            echo "Successfully built and pushed $image_name."
        else
            echo "Failed to push $image_name. Please check your Docker configuration and try again."
            return 1
        fi
    else
        echo "Build failed for $image_name. Skipping push step."
        return 1
    fi
}

case $choice in
    1)
        build_and_push "chat-finn-gpt" "Dockerfile.chat"
        ;;
    2)
        build_and_push "base-finn-gpt" "Dockerfile.base"
        ;;
    3)
        build_and_push "chat-finn-gpt" "Dockerfile.chat"
        build_and_push "base-finn-gpt" "Dockerfile.base"
        ;;
    *)
        echo "Invalid choice. Please run the script again and select 1, 2, or 3."
        exit 1
        ;;
esac

echo "Build and push process completed."