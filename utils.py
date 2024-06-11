import os
from google.cloud import storage

storagebucket = os.environ.get("STORAGE_BUCKET_URI")

def list_blobs(bucket_name = storagebucket):
    """Lists all the blobs in the bucket."""
    # bucket_name = "your-bucket-name"
    storage_client = storage.Client()

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs(bucket_name)
    listofblobs=''
    i=0
    for blob in blobs:
        i=i+1
        listofblobs = f"[{i}] gs://" + blob.bucket.name + "/" + blob.name + '\n'
    return listofblobs

def list_blobs_dialogue(dialogue_data, bucket_name = storagebucket):
    """Lists all the blobs in the bucket."""
    # bucket_name = "your-bucket-name"
    storage_client = storage.Client()

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs(bucket_name)
    for blob in blobs:
        items ={}
        items['text'] = f"gs://" + blob.bucket.name + "/" + blob.name
        items['value'] = f"gs://" + blob.bucket.name + "/" + blob.name + ' ' + blob.content_type
        items['selected'] = False
        dialogue_data["action_response"]["dialog_action"]["dialog"]["body"]["sections"][0]["widgets"][0]["selectionInput"]["items"].append(items)
    
    return dialogue_data