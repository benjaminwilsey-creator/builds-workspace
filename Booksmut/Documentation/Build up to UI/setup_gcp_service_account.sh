#!/bin/bash
# Script to automate Step 0-5: Google Cloud Service Account Setup for ReelForge

echo "--- ReelForge GCP Service Account Setup ---"

# 1. Check for active project
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo "Error: No Google Cloud project selected."
    echo "Please run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

# Get the current user's email
USER_EMAIL=$(gcloud config get-value account)
if [ -z "$USER_EMAIL" ]; then
    echo "Error: Could not determine your GCP user account."
    echo "Please make sure you are logged in with 'gcloud auth login'."
    exit 1
fi

echo "Using Project ID: $PROJECT_ID"
echo "Will grant impersonation rights to: $USER_EMAIL"

SA_NAME="reelforge-api-runner"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Part B: Create the Service Account
echo "Creating Service Account: $SA_NAME..."
gcloud iam service-accounts create $SA_NAME \
    --display-name="Service account for ReelForge pipeline API calls"

# Part C: Assign Permissions
echo "Assigning Roles to Service Account..."
ROLES=(
    "roles/aiplatform.user"
    "roles/serviceusage.serviceUsageConsumer"
)

for ROLE in "${ROLES[@]}"; do
    echo "  Adding $ROLE..."
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SA_EMAIL" \
        --role="$ROLE" \
        --condition=None > /dev/null 2>&1
done

# Part D: Grant Impersonation Role to the User
echo "Granting your account ($USER_EMAIL) permission to impersonate the service account..."
gcloud iam service-accounts add-iam-policy-binding $SA_EMAIL \
    --member="user:$USER_EMAIL" \
    --role="roles/iam.serviceAccountTokenCreator" > /dev/null 2>&1

echo "---"
echo "Setup Complete!"
echo "Service Account Email: $SA_EMAIL"
echo ""
echo "ACTION REQUIRED: No key file was created due to your organization's security policy."
echo "Instead, you have been granted permission to 'impersonate' this service account."
echo ""
echo "To authenticate your local application, run the following command:"
echo "gcloud auth application-default set-impersonation-service-account $SA_EMAIL"
echo ""
echo "This will configure your local environment to use the service account's permissions."
echo "You do not need to manage a JSON key file."