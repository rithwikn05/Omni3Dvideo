
import os   
import re
import json
import requests


def test():
    print("hello")

def get_code_from_gpt(prompt, omniverse_code):

        openai_api_key = "sk-XFbm9kZEDffLd85VzKTAdAqPRV-AOtLJQpeX4Xi_KHT3BlbkFJYW9yCcTjbd0TCLhaWCvU9hYD4r5t6UHuFi_S4gt8wA"# put yout api key here
        if openai_api_key is None:
            raise ValueError("OpenAI API key is not set in environment variables.")

        url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}"
        }

        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": f"You are a coding assistant specialized in understanding natural language instructions and mapping them to specific programming methods. Given a list of available methods, your task is to accurately identify the action to perform, the subject of the action, and determine the most appropriate method to call."
                },
                {
                    "role": "user",
                    "content": f"Please analyze the following instructions: {prompt}. Your task is to: 1. Identify the action to be performed (e.g., zoom, pan). 2. Identify the subject of the action (e.g., battery, screen). 3. Match the identified action and subject to the most appropriate method from the following list of methods: {omniverse_code}. Provide the identified action, subject, and corresponding method in your response all in seperate lines."
                }
            ]
        }

        response = requests.post(url, headers=headers, json=data)

        # Check if the request was successful
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
        else:
            print("Error was got.")


        code_match = re.search(r'```(?:python)?\n([\s\S]*?)```', content)
        code = code_match.group(1) if code_match else content

        if code:
            lines = code.split('\n')
            code_lines = [line for line in lines if line.strip()]
            return '\n'.join(code_lines)
        else:
            return code

# print(get_code_from_gpt("battery"))




    # MODEL = "gpt-3.5-turbo"
    # response = client.chat.completions.create(
    #     model = MODEL,
    #     messages = [
    #        {"role": "system", "content": f"You are a helpful Omniverse OpenUSD code generation assistant. Use {omniverse_code} as a template to help generate the python code to meet the users needs."},
    #        {"role": "user", "content": f"{prompt}. Please provide the code in Python, using the Omniverse OpenUSD API as well as this template code: {omniverse_code}"}
    #     ],
    #     functions = [
    #        {
    #           "name": "generate_code",
    #           "description": "You are a helpful Omniverse OpenUSD code generation assistant",
    #           "parameters": {
    #              "type": "object",
    #              "properties": {
    #                 "code": {
    #                         "type": "string",
    #                         "description": "The generated Python code using the Omniverse OpenUSD API"
    #                     }
    #              },
    #              "required": ["code"]
    #           }
    #        }
    #     ],
    #     function_call = {"name": "generate_code"}
    # )

    # if response.choices[0].message.function_call:
    #     # Extract the code from the function call arguments
    #     function_args = json.loads(response.choices[0].message.function_call.arguments)
    #     code = function_args.get('code', 'No code was generated.')
    # else:
    #     # If no function was called, check for content
    #     content = response.choices[0].message.content
    #     if content:
    #         code_match = re.search(r'```(?:python)?\n([\s\S]*?)```', content)
    #         code = code_match.group(1) if code_match else content
    #     else:
    #         code = "No code or content was generated."

    # Remove comments and empty lines





    ## select cube1
        # selection.set_selected_prim_paths(["/cube1"], True)
        # frame to the selection
#         omni.kit.viewport.utility.frame_viewport_selection(viewport_api=viewport_api)
# selection = viewport_api.usd_context.get_selection()
# viewport_api = viewport_window.viewport_api
# viewport_window = omni.kit.viewport.utility.get_active_viewport_window()


# def focus_on_selected_prim

# omni.kit.commands.execute("DuplicateViewportCameraCommand", viewport_api=viewport_api)