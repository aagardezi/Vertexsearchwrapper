#!/usr/bin/python3

"""
Receives an input chat message via Google Chat, then processes and sends a reply back to the user
"""

import os

from flask import Flask, request
from oauth2client import client

from typing import Any, Mapping


from typing import List

from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.protobuf.json_format import MessageToDict
from urllib.parse import urlparse
from google.cloud import storage

from google.cloud import firestore

import dialoguehelper
import agentsearchhelper
import utils



app = Flask(__name__)

project_id = os.environ.get("PROJECT_ID")
location = "global"          # Values: "global", "us", "eu"
engine_id = os.environ.get("AGENT_ID")
datastore_id = os.environ.get("DATASTORE_ID")

storagebucket = os.environ.get("STORAGE_BUCKET_URI")

topic_id = os.environ.get("TOPIC_ID")
AUDIENCE = os.environ.get('PROJECT_NUMBER')


function_table = {
    '100': utils.list_blobs,
    '200': agentsearchhelper.createconversation, #multi turn chat start
    '210': agentsearchhelper.stopconversation, #multi turn chat stop
    '500': dialoguehelper.open_gemini_qa_dialogue,
    '501': dialoguehelper.open_gemini_fileqa_dialogue,
    '502': dialoguehelper.open_gemini_qa_dialogue_grounded,
    '503': dialoguehelper.open_gemini_filecompare_dialogue,
}






@app.route('/', methods=['POST'])
def handler():
    # Retrieve JSON input from request body
    event_data = request.get_json(silent=False)
    # json_formatted_str = json.dumps(event_data, indent=0)
    # print(json_formatted_str)

    # Verify request is sourced from Google Chat - https://developers.google.com/chat/api/guides/message-formats
    CHAT_ISSUER = 'chat@system.gserviceaccount.com'
    PUBLIC_CERT_URL_PREFIX = 'https://www.googleapis.com/service_accounts/v1/metadata/x509/'
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

    cardresponse, card_clicked_flag = dialoguehelper.handle_card_clicked(event_data, project_id, topic_id)
    if card_clicked_flag:
        return cardresponse
    
    #username of the current chat user so we can start a conversation thread for multi turn
    username = event_data["user"]["name"].split('/')[1]
    
    if slash_command := event_data.get('message', dict()).get('slashCommand'):
        command_id = slash_command['commandId']
        if int(command_id) == 200:
            return {'text': function_table[str(command_id)](username)}, 200
        if int(command_id) == 210:
            return {'text': function_table[str(command_id)](username)}, 200
        if int(command_id) >= 500:
            if int(command_id) == 501:
                return utils.list_blobs_dialogue(function_table[str(command_id)]())
            elif int(command_id) == 503:
                return utils.list_blobs_dialogue(function_table[str(command_id)]())
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
        if agentsearchhelper.conversationexists(username):
            return agentsearchhelper.search_conversation(text, username)
    
        answer = agentsearchhelper.search_simple(text)
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
