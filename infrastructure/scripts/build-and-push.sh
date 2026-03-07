#!/usr/bin/env bash
# Build the Docker image and push it to ECR.
# Run from the project root: ./infrastructure/scripts/build-and-push.sh
set -euo pipefail

REGION="us-west-2"
ENVIRONMENT="${1:-dev}"

# Resolve ECR URL from Terraform output
ECR_URL=$(cd infrastructure/terraform/environments/${ENVIRONMENT} && terraform output -raw ecr_repository_url)
TAG="${ECR_URL}:latest"

echo "→ Authenticating with ECR..."
aws ecr get-login-password --region "$REGION" | \
  docker login --username AWS --password-stdin "$ECR_URL"

echo "→ Building image: $TAG"
docker build --platform linux/amd64 -t "$TAG" .

echo "→ Pushing image: $TAG"
docker push "$TAG"

echo "→ Forcing ECS service redeployment..."
CLUSTER=$(cd infrastructure/terraform/environments/${ENVIRONMENT} && terraform output -raw ecs_cluster)
SERVICE=$(cd infrastructure/terraform/environments/${ENVIRONMENT} && terraform output -raw ecs_service)
aws ecs update-service \
  --region "$REGION" \
  --cluster "$CLUSTER" \
  --service "$SERVICE" \
  --force-new-deployment \
  --query "service.serviceName" \
  --output text

echo "✓ Done. Monitor deployment:"
echo "  aws ecs describe-services --region $REGION --cluster $CLUSTER --services $SERVICE --query 'services[0].deployments'"
