# Vertexsearchwrapper

This is a wrapper to call the Vertex Search API and get a response that can be sent to a Google Chat API Bot

## Getting started

Start by creating a serach app in Vertex AI Search & Conversation. Once you have created the app you need the folloing
info to access and setup this container as a cloud run function:

GCP Project ID
GCP Project Number
Agent ID (Vertex AI Search App ID)


## Instructions for creating the Cloud Run APP
```
gcloud iam service-accounts create chatbot-handler --description="Receives and processes events from Google Chat" --display-name="Chatbot handler"
```
```
gcloud projects add-iam-policy-binding [PROJECT_ID] --member="serviceAccount:chatbot-handler@[PROJECT_ID].iam.gserviceaccount.com" --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding [PROJECT_ID] --member="serviceAccount:chatbot-handler@[PROJECT_ID].iam.gserviceaccount.com" --role="roles/discoveryengine.admin"

gcloud projects add-iam-policy-binding [PROJECT_ID] --member="serviceAccount:chatbot-handler@[PROJECT_ID].iam.gserviceaccount.com" --role="roles/storage.objectViewer"
```
```
gcloud run deploy chat-handler --image=gcr.io/genaillentsearch/gitlab.com/google-cloud-ce/googlers/sgardezi/vertexsearchwrapper:latest --allow-unauthenticated --set-env-vars=PROJECT_ID=[PROJECT_ID],PROJECT_NUMBER=[PROJECT_NUMBER],AGENT_ID=[VERTEX_APP_ID],STORAGE_BUCKET_URI=[BUCKET_NAME],TOPIC_ID=[TOPIC] --region=us-west1 --service-account=chatbot-handler@[PROJECT_ID].iam.gserviceaccount.com
```
