#!/bin/bash

# Build and push Docker image
echo "🐳 Building and pushing Docker image..."

DOCKER_USERNAME="algsoch"
IMAGE_NAME="prompt-template-studio"
TAG="latest"

# Login to Docker Hub
echo "🔐 Logging in to Docker Hub..."
docker login --username $DOCKER_USERNAME

# Build the image
echo "🔨 Building Docker image..."
docker build -t $DOCKER_USERNAME/$IMAGE_NAME:$TAG .

# Tag with additional version
VERSION=$(date +%Y%m%d-%H%M%S)
docker tag $DOCKER_USERNAME/$IMAGE_NAME:$TAG $DOCKER_USERNAME/$IMAGE_NAME:$VERSION

# Push to Docker Hub
echo "📤 Pushing to Docker Hub..."
docker push $DOCKER_USERNAME/$IMAGE_NAME:$TAG
docker push $DOCKER_USERNAME/$IMAGE_NAME:$VERSION

echo "✅ Docker image pushed successfully!"
echo "📦 Image: $DOCKER_USERNAME/$IMAGE_NAME:$TAG"
echo "📦 Version: $DOCKER_USERNAME/$IMAGE_NAME:$VERSION"

echo ""
echo "🚀 To run the container locally:"
echo "docker run -p 8000:8000 --env-file .env $DOCKER_USERNAME/$IMAGE_NAME:$TAG"

echo ""
echo "🌐 To deploy on various platforms:"
echo "• DigitalOcean: Use App Platform with Docker image"
echo "• AWS: Use ECS, EKS, or App Runner"
echo "• GCP: Use Cloud Run or GKE"
echo "• Azure: Use Container Instances or AKS"