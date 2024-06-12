# Vertexsearchwrapper

This is a wrapper to call the Vertex Search API and get a response that can be sent to a Google Chat API Bot

## Getting started

Start by creating a serach app in Vertex AI Search & Conversation. Once you have created the app you need the folloing
info to access and setup this container as a cloud run function:

GCP Project ID
GCP Project Number
Agent ID (Vertex AI Search App ID)


## Instructions to Enable GCP APIs

```
gcloud config set project YOUR_PROJECT_ID
```

Enable Cloud Run APIs
```
gcloud services enable run.googleapis.com
```

Enable Cloud Function APIs
```
gcloud services enable \
    cloudfunctions.googleapis.com \
    cloudbuild.googleapis.com
```


Enable Vertex AI and Agent Builder APIs
```
gcloud services enable \
    aiplatform.googleapis.com \
    cloudbuild.googleapis.com \
    compute.googleapis.com \
    containerregistry.googleapis.com \
    artifactregistry.googleapis.com
```

```
gcloud services enable \
    aiplatform.googleapis.com \
    generativelanguage.googleapis.com \
    dialogflow.googleapis.com  
```

```
gcloud services enable \
    discoveryengine.googleapis.com  # For using Discovery Engine
```



## Instructions for creating the Cloud Run APP
```
gcloud iam service-accounts create chatbot-handler --description="Receives and processes events from Google Chat" --display-name="Chatbot handler"
```
```
gcloud projects add-iam-policy-binding [PROJECT_ID] --member="serviceAccount:chatbot-handler@[PROJECT_ID].iam.gserviceaccount.com" --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding [PROJECT_ID] --member="serviceAccount:chatbot-handler@[PROJECT_ID].iam.gserviceaccount.com" --role="roles/discoveryengine.admin"

gcloud projects add-iam-policy-binding [PROJECT_ID] --member="serviceAccount:chatbot-handler@[PROJECT_ID].iam.gserviceaccount.com" --role="roles/storage.objectViewer"

gcloud projects add-iam-policy-binding [PROJECT_ID] --member="serviceAccount:chatbot-handler@[PROJECT_ID].iam.gserviceaccount.com" --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding [PROJECT_ID] --member="serviceAccount:chatbot-handler@[PROJECT_ID].iam.gserviceaccount.com" --role="roles/chat.owner"

gcloud projects add-iam-policy-binding [PROJECT_ID] --member="serviceAccount:chatbot-handler@[PROJECT_ID].iam.gserviceaccount.com" --role="roles/cloudfunctions.serviceAgent"

gcloud projects add-iam-policy-binding [PROJECT_ID] --member="serviceAccount:chatbot-handler@[PROJECT_ID].iam.gserviceaccount.com" --role="roles/pubsub.publisher"

gcloud projects add-iam-policy-binding [PROJECT_ID] --member="serviceAccount:chatbot-handler@[PROJECT_ID].iam.gserviceaccount.com" --role="roles/pubsub.subscriber"

gcloud projects add-iam-policy-binding [PROJECT_ID] --member="serviceAccount:chatbot-handler@[PROJECT_ID].iam.gserviceaccount.com" --role="roles/run.invoker"

gcloud projects add-iam-policy-binding [PROJECT_ID] --member="serviceAccount:chatbot-handler@[PROJECT_ID].iam.gserviceaccount.com" --role="roles/datastore.user"
```

## Create topic for function trigger
```
gcloud pubsub topics create [TOPIC]
```

## Instructions for deploying the Cloud Run APP
```
gcloud run deploy chat-handler --image=gcr.io/genaillentsearch/gitlab.com/google-cloud-ce/googlers/sgardezi/vertexsearchwrapper:latest --allow-unauthenticated --set-env-vars=PROJECT_ID=[PROJECT_ID],PROJECT_NUMBER=[PROJECT_NUMBER],AGENT_ID=[VERTEX_APP_ID],STORAGE_BUCKET_URI=[BUCKET_NAME],TOPIC_ID=[TOPIC],DATASTORE_ID=[DATASTORE_ID] --region=us-west1 --service-account=chatbot-handler@[PROJECT_ID].iam.gserviceaccount.com
```
