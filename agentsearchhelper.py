import os

from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.protobuf.json_format import MessageToDict
from urllib.parse import urlparse
from google.cloud import storage

from google.cloud import firestore
from datetime import datetime

project_id = os.environ.get("PROJECT_ID")
location = "global"          # Values: "global", "us", "eu"
engine_id = os.environ.get("AGENT_ID")
datastore_id = os.environ.get("DATASTORE_ID")

storagebucket = os.environ.get("STORAGE_BUCKET_URI")

topic_id = os.environ.get("TOPIC_ID")

def createconversation(username):
    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
        if location != "global"
        else None
    )

    # Create a client
    client = discoveryengine.ConversationalSearchServiceClient(
        client_options=client_options
    )

    # Initialize Multi-Turn Session
    conversation = client.create_conversation(
        # The full resource name of the data store
        # e.g. projects/{project_id}/locations/{location}/dataStores/{data_store_id}
        parent=client.data_store_path(
            project=project_id, location=location, data_store=datastore_id
        ),
        conversation=discoveryengine.Conversation(),
    )

    db = firestore.Client()

    # Reference to a collection
    users_ref = db.collection(u'chatconversations')

    timestamp = datetime.utcnow().isoformat()

    # Add a document
    data = {
        u'username': username,
        u'conversationname': conversation.name,
        u'timestamp': timestamp
    }
    print(username)
    print(conversation.name)
    users_ref.document(username).set(data)
    return f"Conversation created {conversation.name}"

def conversationexists(username):
    db = firestore.Client()
    doc = db.collection(u'chatconversations').document(username).get()
    if doc.exists:
        return True
    return False

def search_conversation(prompt, username):
    db = firestore.Client()
    doc = db.collection(u'chatconversations').document(username).get()
    if doc.exists:
        client_options = (
            ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
            if location != "global"
            else None
        )

        # Create a client
        client = discoveryengine.ConversationalSearchServiceClient(
            client_options=client_options
        )
        request = discoveryengine.ConverseConversationRequest(
            name=doc.to_dict().get('conversationname'),
            query=discoveryengine.TextInput(input=prompt),
            serving_config=client.serving_config_path(
                project=project_id,
                location=location,
                data_store=datastore_id,
                serving_config="default_config",
            ),
            # Options for the returned summary
            summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                # Number of results to include in summary
                summary_result_count=10,
                include_citations=True,
                model_prompt_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelPromptSpec(
                preamble="make sure you evaluate a full name before answering questions regarding named individuals. If the exact named individual is not found say you dont know. Also any question where you are not confident of the answer do not make up an answer. Make sure the result has formatting."
                ),
                model_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelSpec(
                    version="preview",
                ),
            ),
        )
        response = client.converse_conversation(request)

        # filelist = ''
        # for i, result in enumerate(response.search_results, 1):
        #     result_data = result.document.derived_struct_data
        #     filelist = filelist +'\n' + f'[{i}] ' + result_data['link']

        #above code has been refactored into a funciton that can be used with all outputs
        filelist = format_links(response.search_results)

        return {'text': response.reply.summary.summary_text+ '\n' + filelist }, 200


def stopconversation(username):
     db = firestore.Client()
     doc = db.collection(u'chatconversations').document(username).delete()
     return "Conversation delete"

def search_simple(
    prompt: str,
):
    #  For more information, refer to:
    # https://cloud.google.com/generative-ai-app-builder/docs/locations#specify_a_multi-region_for_your_data_store
    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
        if location != "global"
        else None
    )

    # Create a client
    client = discoveryengine.SearchServiceClient(client_options=client_options)

    # The full resource name of the search app serving config
    serving_config = f"projects/{project_id}/locations/{location}/collections/default_collection/engines/{engine_id}/servingConfigs/default_config"

    # Optional: Configuration options for search
    # Refer to the `ContentSearchSpec` reference for all supported fields:
    # https://cloud.google.com/python/docs/reference/discoveryengine/latest/google.cloud.discoveryengine_v1.types.SearchRequest.ContentSearchSpec
    content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
        # For information about snippets, refer to:
        # https://cloud.google.com/generative-ai-app-builder/docs/snippets
        snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
            return_snippet=True
        ),
        # For information about search summaries, refer to:
        # https://cloud.google.com/generative-ai-app-builder/docs/get-search-summaries
        summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
            summary_result_count=10,
            include_citations=True,
            ignore_adversarial_query=True,
            ignore_non_summary_seeking_query=True,
            model_prompt_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelPromptSpec(
                preamble="make sure you evaluate a full name before answering questions regarding named individuals. If the exact named individual is not found say you dont know. Also any question where you are not confident of the answer do not make up an answer. Make sure the result has formatting."
            ),
            model_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelSpec(
                version="preview",
            ),
        ),
        extractive_content_spec = discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
            max_extractive_answer_count = 1
        ),
    )

    # Refer to the `SearchRequest` reference for all supported fields:
    # https://cloud.google.com/python/docs/reference/discoveryengine/latest/google.cloud.discoveryengine_v1.types.SearchRequest
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=prompt,
        page_size=10,
        content_search_spec=content_search_spec,
        query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
            condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
        ),
        spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
            mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
        ),
    )

    response = client.search(request)
    filelist = format_links(response.search_results)
    # i=0
    # for result in response.results:
    #     i=i+1
    #     if i>5:
    #         break
    #     document_dict = MessageToDict(
    #         result.document._pb, preserving_proto_field_name=True
    #     )
    #     derived_struct_data = document_dict.get("derived_struct_data")
    #     filelist = filelist + '\n' + f'[{i}] https://storage.cloud.google.com/' + urlparse(derived_struct_data.get("link", "")).hostname + urlparse(derived_struct_data.get("link", "")).path

    # print(response.summary.summary_text)
    return response.summary.summary_text + '\n' + filelist 

def format_links(results):
    filelist = ''
    for i, result in enumerate(results, 1):
        result_data = result.document.derived_struct_data
        filelist = filelist +'\n' + f'[{i}] https://storage.cloud.google.com/' + urlparse(result_data['link']).hostname + urlparse(result_data['link']).path
    return filelist