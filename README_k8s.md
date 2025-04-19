# FastAPI GKE Deployment

This document follows [README.md](README.md) with container image availabe
from dockerhub.

## workload identity for application KSA

It is best practice to set Workload Identity between the application-specific
Kubernetes ServiceAccount (KSA) and GCP ServiceAccount (GSA).

-   The KSA is created by `k8s/service-account.yaml`.
-   The GSA is provided by cluster (node-sa@$PROJECT_ID.iam.gserviceaccount.com).

```sh
PROJECT_ID=poc-data-platform-289915
CLUSTER_SERVICE_ACCOUNT=node-sa@$PROJECT_ID.iam.gserviceaccount.com
KSA_NAME=todo-api-sa
KSA_NAMESPACE=todo-api

# Create IAM binding between K8s ServiceAccount and GCP ServiceAccount
gcloud iam service-accounts add-iam-policy-binding $CLUSTER_SERVICE_ACCOUNT \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:$PROJECT_ID.svc.id.goog[$KSA_NAMESPACE/$KSA_NAME]" \
```

This allows the Kubernetes ServiceAccount `todo-api-sa` in namespace `todo-api`
to act as the GCP service account node-sa.

**NOTE:** This IAM binding **must** be done before deploying the k8s service 
account.

## Create GCP secrets for the application

First create the required secrets in Google Secret Manager, otherwise
the secrets.yaml deployment will fail.

```sh
# Create the secrets in Google Secret Manager
echo -n "postgresql://user:password@db-service:3306/todoapp" | \
  gcloud secrets create DATABASE_URL --data-file=-

echo -n "your-api-key-value" | \
  gcloud secrets create API_KEY --data-file=-

# check the secrets
gcloud secrets versions access latest --secret="DATABASE_URL"
gcloud secrets versions access latest --secret="API_KEY"
```

## Deploy the application:

```sh
# deploy k8s resources
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/service-account.yaml
kubectl apply -f k8s/configmap.yaml
# kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml
```

## Check workload identity

To check if the pod can access GCP resources, run a debugging pod with
the kubernetes service account, and test access GCP secrets:

```sh
# verify the binding
kubectl describe serviceaccount todo-api-sa -n todo-api

# Start a debugging pod with the service account
# Note the use of --overrides to set the service account
kubectl run -it --rm debug --image=google/cloud-sdk:slim \
  --overrides='{"spec":{"serviceAccountName":"todo-api-sa"}}' \
  -n todo-api -- bash

# Then from inside the pod, try accessing a secret:
gcloud secrets versions access latest --secret="API_KEY"
```

## Access the FastAPI App via Public Ingress

First verify cluster Nginx ingress controller:

```sh
kubectl get service --namespace ingress-nginx ingress-nginx-controller
```

Then verify application ingress:

```sh
kubectl describe ingress todo-api-ingress -n todo-api

# grep for the IP address and assign to a variable
EXTERNAL_IP=$(kubectl get ingress todo-api-ingress -n todo-api \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Ingress external IP: ${EXTERNAL_IP}"

# call the health endpoint via curl
curl http://$EXTERNAL_IP/health | jq

# get openapi.json
curl http://$EXTERNAL_IP/openapi.json | jq
```
