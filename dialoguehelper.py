from typing import Any, Mapping

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