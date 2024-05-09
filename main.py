#!/usr/bin/python3

"""
Receives an input chat message via Google Chat, then processes and sends a reply back to the user
"""

import json
import os
import uuid

from flask import Flask, request
from oauth2client import client

from typing import Any, Mapping


from typing import List

from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.protobuf.json_format import MessageToDict
from urllib.parse import urlparse
from google.cloud import storage

import dialoguehelper
import geminihelper



app = Flask(__name__)

project_id = os.environ.get("PROJECT_ID")
location = "global"          # Values: "global", "us", "eu"
engine_id = os.environ.get("AGENT_ID")

storagebucket = os.environ.get("STORAGE_BUCKET_URI")

topic_id = os.environ.get("TOPIC_ID")



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
    listofblobs=''
    i=0
    for blob in blobs:
        items ={}
        items['text'] = f"gs://" + blob.bucket.name + "/" + blob.name
        items['value'] = f"gs://" + blob.bucket.name + "/" + blob.name + ' ' + blob.content_type
        items['selected'] = False
        dialogue_data["action_response"]["dialog_action"]["dialog"]["body"]["sections"][0]["widgets"][0]["selectionInput"]["items"].append(items)
    
    return dialogue_data

function_table = {
    '100': list_blobs,
    '500': dialoguehelper.open_gemini_qa_dialogue,
    '501': dialoguehelper.open_gemini_fileqa_dialogue,
    '502': dialoguehelper.open_gemini_qa_dialogue_grounded,
    '503': dialoguehelper.open_gemini_filecompare_dialogue,
}

def search_sample(
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
            summary_result_count=5,
            include_citations=True,
            ignore_adversarial_query=True,
            ignore_non_summary_seeking_query=True,
            # model_prompt_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelPromptSpec(
            #     preamble="YOUR_CUSTOM_PROMPT"
            # ),
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
    filelist = ''
    i=0
    for result in response.results:
        i=i+1
        if i>5:
            break
        document_dict = MessageToDict(
            result.document._pb, preserving_proto_field_name=True
        )
        derived_struct_data = document_dict.get("derived_struct_data")
        filelist = filelist + '\n' + f'[{i}] https://storage.cloud.google.com/' + urlparse(derived_struct_data.get("link", "")).hostname + urlparse(derived_struct_data.get("link", "")).path

    # print(response.summary.summary_text)
    return response.summary.summary_text + '\n' + filelist 

def handle_card_clicked(event_data):
    if event_data.get('type') == 'CARD_CLICKED':
        invoked_function = event_data.get('common', dict()).get('invokedFunction')
        if invoked_function == 'ask_gemini':
            if common := event_data.get('common'):
                if form_inputs := common.get('formInputs'):
                    if contact_name := form_inputs.get('llm_question'):
                        if string_inputs := contact_name.get('stringInputs'):
                            if llm_question := string_inputs.get('value')[0]:
                                response_message = geminihelper.generate(project_id, llm_question)
                                return {
                                    "actionResponse": {
                                        "type": "NEW_MESSAGE",
                                    },
                                    "text": f"{response_message}",
                                }, True
        
        if invoked_function == 'ask_gemini_file':
            if common := event_data.get('common'):
                if form_inputs := common.get('formInputs'):
                    if contact_name := form_inputs.get('llm_question'):
                        if string_inputs := contact_name.get('stringInputs'):
                            if llm_question := string_inputs.get('value')[0]:
                                filepath = form_inputs.get('filename').get('stringInputs').get('value')[0]
                                space_name = event_data['space']['name']
                                geminihelper.publish_gemini_message(project_id, topic_id, llm_question, filepath, space_name)
                                return {
                                    "actionResponse": {
                                        "type": "NEW_MESSAGE",
                                    },
                                    "text": f"{llm_question}\nRequest submitted, awaiting response... :gemini-animated:",
                                }, True
        if invoked_function == 'ask_gemini_filecompare':
            if common := event_data.get('common'):
                if form_inputs := common.get('formInputs'):
                    if contact_name := form_inputs.get('llm_question'):
                        if string_inputs := contact_name.get('stringInputs'):
                            if llm_question := string_inputs.get('value')[0]:
                                filepath1 = form_inputs.get('filename').get('stringInputs').get('value')[0]
                                filepath2 = form_inputs.get('filename').get('stringInputs').get('value')[1]
                                print(form_inputs.get('filename'))
                                space_name = event_data['space']['name']
                                geminihelper.publish_gemini_compare_message(project_id, topic_id, llm_question, filepath1, filepath2, space_name)
                                return {
                                    "actionResponse": {
                                        "type": "NEW_MESSAGE",
                                    },
                                    "text": f"{llm_question}\nRequest submitted, awaiting response... :gemini-animated:",
                                }, True
        if invoked_function == 'ask_gemini_grounded':
            if common := event_data.get('common'):
                if form_inputs := common.get('formInputs'):
                    if contact_name := form_inputs.get('llm_question'):
                        if string_inputs := contact_name.get('stringInputs'):
                            if llm_question := string_inputs.get('value')[0]:
                                response_message = geminihelper.generate_grounded(project_id, llm_question)
                                return {
                                    "actionResponse": {
                                        "type": "NEW_MESSAGE",
                                    },
                                    "text": f"{response_message}",
                                }, True
    return {}, False


@app.route('/', methods=['POST'])
def handler():
    # Retrieve JSON input from request body
    event_data = request.get_json(silent=False)
    # json_formatted_str = json.dumps(event_data, indent=0)
    # print(json_formatted_str)

    # Verify request is sourced from Google Chat - https://developers.google.com/chat/api/guides/message-formats
    CHAT_ISSUER = 'chat@system.gserviceaccount.com'
    PUBLIC_CERT_URL_PREFIX = 'https://www.googleapis.com/service_accounts/v1/metadata/x509/'
    AUDIENCE = os.environ.get('PROJECT_NUMBER')
    BEARER_TOKEN = request.headers['Authorization'].replace('Bearer ', '')
    try:
        token = client.verify_id_token(BEARER_TOKEN, AUDIENCE, cert_uri=PUBLIC_CERT_URL_PREFIX + CHAT_ISSUER)
        if token['iss'] != CHAT_ISSUER:
            return 'Invalid issuee', 401
    except:
        return 'Invalid token', 401

    # Return error if payload has invalid data
    if 'space' not in event_data:
        return 'This service only processes events sent from Google Chat', 400

    cardresponse, card_clicked_flag = handle_card_clicked(event_data)
    if card_clicked_flag:
        return cardresponse
    
                                

    
    if slash_command := event_data.get('message', dict()).get('slashCommand'):
        command_id = slash_command['commandId']
        if int(command_id) >= 500:
            if int(command_id) == 501:
                return list_blobs_dialogue(function_table[str(command_id)]())
            elif int(command_id) == 503:
                return list_blobs_dialogue(function_table[str(command_id)]())
            else:
                return function_table[str(command_id)]()
        else:
            return {'text': function_table[str(command_id)]()}, 200





    # Parse message text/components
    text = first = None
    if 'message' in event_data and 'argumentText' in event_data['message']:  # for space/room
        text = event_data['message']['argumentText'].strip()
    elif 'message' in event_data and 'text' in event_data['message']:  # for direct message
        text = event_data['message']['text'].strip()
    if text:
        first = text.split()[0].lower()

    # Print help message
    if first in ('?', 'hi', 'hello', 'help', 'hey', 'start', 'test', '/help'):
        if event_data['space']['type'] == 'DM':
            name = event_data['user']['displayName'].split()[0]
        else:  # 'ROOM'
            name = f'<{event_data["user"]["name"]}>'  # 'users/[USER_ID]'
        output_message = f'Hi *{name}*! As a demo, ask a question on the data trained for the bot.'

    # Query Vertex Search app
    else:
        answer = search_sample(text)
        #responses = answer['responseMessages']
        #output_message = responses[0]['text']['text'][0]
        output_message = answer

        if output_message == 'Indexing didn\'t finish yet, please come back in a few hours.':
            output_message = 'Sorry, I can\'t help you with that.'
        # elif len(responses) > 1 and 'payload' in responses[1]:
        #     content = responses[1]['payload']['richContent'][0][0]
        #     action_link = None
        #     for k, v in content.items():
        #         if k == 'actionLink':
        #             action_link = v
        #             break
        #     output_message += f'\n{action_link}'

    return {'text': output_message}, 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
