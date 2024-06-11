from typing import Any, Mapping
import geminihelper

def open_gemini_qa_dialogue() -> Mapping[str, Any]:
    return {
    'action_response': {
      'type': 'DIALOG',
      'dialog_action': {
        'dialog': {
          'body':{
            "sections": [
                {
                "header": "Ask Gemini a Question",
                "widgets": [
                    {
                    "textInput": {
                        "name": "llm_question",
                        "label": "Question for Gemini 1.5"
                    }
                    },
                    {
                    "buttonList": {
                        "buttons": [
                        {
                            "text": "Ask Gemini 1.5",
                            "color": {
                            "alpha": 1
                            },
                            "onClick": {
                            "action": {
                                "function": "ask_gemini"
                            }
                            },
                            "disabled": False
                        }
                        ]
                    }
                    }
                ]
                }
            ]
            }}}}}

def open_gemini_qa_dialogue_grounded() -> Mapping[str, Any]:
    return {
    'action_response': {
      'type': 'DIALOG',
      'dialog_action': {
        'dialog': {
          'body':{
            "sections": [
                {
                "header": "Ask Gemini a Question",
                "widgets": [
                    {
                    "textInput": {
                        "name": "llm_question",
                        "label": "Question for Gemini 1.5"
                    }
                    },
                    {
                    "buttonList": {
                        "buttons": [
                        {
                            "text": "Ask Gemini 1.5",
                            "color": {
                            "alpha": 1
                            },
                            "onClick": {
                            "action": {
                                "function": "ask_gemini_grounded"
                            }
                            },
                            "disabled": False
                        }
                        ]
                    }
                    }
                ]
                }
            ]
            }}}}}

def open_gemini_fileqa_dialogue() -> Mapping[str, Any]:
    return {
    'action_response': {
      'type': 'DIALOG',
      'dialog_action': {
        'dialog': {
          'body':{
            "sections": [
                {
                "header": "Ask Gemini a Question about a file",
                "widgets": [
                    {
                        "selectionInput": {
                            "name": "filename",
                            "label": "File Name",
                            "type": "DROPDOWN",
                            "items": []
                        }
                    },
                    {
                    "textInput": {
                        "name": "llm_question",
                        "label": "Question for Gemini 1.5"
                    }
                    },
                    {
                    "buttonList": {
                        "buttons": [
                        {
                            "text": "Ask Gemini 1.5",
                            "color": {
                            "alpha": 1
                            },
                            "onClick": {
                            "action": {
                                "function": "ask_gemini_file"
                            }
                            },
                            "disabled": False
                        }
                        ]
                    }
                    }
                ]
                }
            ]
            }}}}}

def open_gemini_filecompare_dialogue() -> Mapping[str, Any]:
    return {
    'action_response': {
      'type': 'DIALOG',
      'dialog_action': {
        'dialog': {
          'body':{
            "sections": [
                {
                "header": "Ask Gemini a Question about a file",
                "widgets": [
                    {
                        "selectionInput": {
                            "type": "MULTI_SELECT",
                            "name": "filename",
                            "label": "File Name",
                            "multiSelectMaxSelectedItems": 2,
                            "multiSelectMinQueryLength": 2,
                            "items": []
                        }
                    },
                    {
                    "textInput": {
                        "name": "llm_question",
                        "label": "Question for Gemini 1.5"
                    }
                    },
                    {
                    "buttonList": {
                        "buttons": [
                        {
                            "text": "Ask Gemini 1.5",
                            "color": {
                            "alpha": 1
                            },
                            "onClick": {
                            "action": {
                                "function": "ask_gemini_filecompare"
                            }
                            },
                            "disabled": False
                        }
                        ]
                    }
                    }
                ]
                }
            ]
            }}}}}

def handle_card_clicked(event_data, project_id, topic_id):
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