from openai import OpenAI
import os   
import re
import json

def get_code_from_gpt(prompt, omniverse_code):
    MODEL = "gpt-3.5-turbo"
    response = client.chat.completions.create(
        model = MODEL,
        messages = [
           {"role": "system", "content": f"You are a helpful Omniverse OpenUSD code generation assistant. Use {omniverse_code} as a template to help generate the python code to meet the users needs."},
           {"role": "user", "content": f"{prompt}. Please provide the code in Python, using the Omniverse OpenUSD API as well as this template code: {omniverse_code}"}
        ],
        functions = [
           {
              "name": "generate_code",
              "description": "You are a helpful Omniverse OpenUSD code generation assistant",
              "parameters": {
                 "type": "object",
                 "properties": {
                    "code": {
                            "type": "string",
                            "description": "The generated Python code using the Omniverse OpenUSD API"
                        }
                 },
                 "required": ["code"]
              }
           }
        ],
        function_call = {"name": "generate_code"}
    )

    if response.choices[0].message.function_call:
        # Extract the code from the function call arguments
        function_args = json.loads(response.choices[0].message.function_call.arguments)
        code = function_args.get('code', 'No code was generated.')
    else:
        # If no function was called, check for content
        content = response.choices[0].message.content
        if content:
            code_match = re.search(r'```(?:python)?\n([\s\S]*?)```', content)
            code = code_match.group(1) if code_match else content
        else:
            code = "No code or content was generated."

    # Remove comments and empty lines
    if code and code != "No code or content was generated.":
        lines = code.split('\n')
        code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        return '\n'.join(code_lines)
    else:
        return code

    # return response['choices'][0]['message']['content']

password = ""
os.environ["OPENAI_API_KEY"] = password
client = OpenAI()

print(get_code_from_gpt("Give me code to generate a chair in Omniverse OpenUSD Composer"))