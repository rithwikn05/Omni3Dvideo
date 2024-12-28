
import os   
import re
import json # TODO: unused import?
import requests

# TODO: move out of UsdMethods, isn't really related to USD in general? its just LLM stuff, wrapper for GPT API to remove that responsibility from other parts of your code

class GPTCoder:
    OPENAI_CHAT_COMPETIONS_URL = "https://api.openai.com/v1/chat/completions"

    def __init__(self):
        # ideally, we don't store the api key as an instance variable bc that's a security risk
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key is None:
            raise ValueError("No OpenAI API key was provided!")
    
    def get_code(prompt, omniverse_code):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}"
        }

        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": f"You are a coding assistant specialized in understanding natural language instructions and mapping them to specific programming methods. Given a list of available methods, your task is to accurately identify a sequence of actions to perform, the subject of each action, and determine the most appropriate sequence of methods to call."
                },
                { # TODO: not sure if this is necessary?
                    "role": "assistant",
                    "content": ""
                },
                {
                    "role": "user",
                    "content": f"Please analyze the following instructions: {prompt}. Your task is to: 1. Identify a sequence of actions to be performed (e.g., zoom, pan). 2. Identify the subject of each action (e.g., battery, screen). 3. Match each identified action and subject to the most appropriate method from the following list of methods: {omniverse_code}. Provide the list of identified actions, subjects, and corresponding methods in your response all in seperate lines." # TODO: update for few-shot prompting
                }
            ]
        }

        response = requests.post(GPTCoder.OPENAI_CHAT_COMPETIONS_URL, headers=headers, json=data)

        # Check if the request was successful
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
        else:
            print("[ERROR] GPTCoder: OpenAI HTTP response status code is not 200... got:", response.status_code)

        # find code
        code_match = re.search(r'```(?:python)?\n([\s\S]*?)```', content)
        code = code_match.group(1) if code_match else content

        if code: # parse code
            lines = code.split('\n')
            code_lines = [line for line in lines if line.strip()]
            return '\n'.join(code_lines)
        else:
            return code