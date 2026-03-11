#!/usr/bin/env bash
# Build both Docker images and push them to ECR, then force ECS redeployment.
# Usage (from project root):
#   ./infrastructure/scripts/build-and-push.sh [dev]   # default: dev
set -euo pipefail

REGION="us-west-2"
ENVIRONMENT="${1:-dev}"
TF_DIR="infrastructure/terraform/environments/${ENVIRONMENT}"

tf_output() { (cd "$TF_DIR" && terraform output -raw "$1"); }

echo "→ Fetching ECR URLs from Terraform..."
BACKEND_ECR=$(tf_output ecr_repository_url)
FRONTEND_ECR=$(tf_output ecr_frontend_repository_url)
CLUSTER=$(tf_output ecs_cluster)
BACKEND_SVC=$(tf_output ecs_service)
FRONTEND_SVC=$(tf_output ecs_frontend_service)

echo "→ Authenticating with ECR..."
aws ecr get-login-password --region "$REGION" | \
  docker login --username AWS --password-stdin "$BACKEND_ECR"

# ── Backend ────────────────────────────────────────────────────────────────────
BACKEND_TAG="${BACKEND_ECR}:latest"
echo "→ Building backend: $BACKEND_TAG"
docker build --platform linux/amd64 -t "$BACKEND_TAG" .

echo "→ Pushing backend..."
docker push "$BACKEND_TAG"

# ── Frontend ───────────────────────────────────────────────────────────────────
FRONTEND_TAG="${FRONTEND_ECR}:latest"
echo "→ Building frontend: $FRONTEND_TAG"
# NEXT_PUBLIC_API_URL="" → relative URLs; ALB routes /api/v1/* to the backend
docker build --platform linux/amd64 \
  --build-arg NEXT_PUBLIC_API_URL="" \
  -t "$FRONTEND_TAG" \
  frontend/

echo "→ Pushing frontend..."
docker push "$FRONTEND_TAG"

# ── Force redeployment ────────────────────────────────────────────────────────
deploy_service() {
  local svc="$1"
  aws ecs update-service \
    --region "$REGION" \
    --cluster "$CLUSTER" \
    --service "$svc" \
    --force-new-deployment \
    --query "service.serviceName" \
    --output text
}

echo "→ Redeploying backend service..."
deploy_service "$BACKEND_SVC"

echo "→ Redeploying frontend service..."
deploy_service "$FRONTEND_SVC"

echo ""
echo "✓ Done. Monitor deployments:"
echo "  aws ecs describe-services --region $REGION --cluster $CLUSTER \\"
echo "    --services $BACKEND_SVC $FRONTEND_SVC \\"
echo "    --query 'services[*].{name:serviceName,running:runningCount,deployments:deployments[0].rolloutState}'"
