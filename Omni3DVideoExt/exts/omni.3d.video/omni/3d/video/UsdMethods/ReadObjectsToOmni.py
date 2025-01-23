import re
import ast

from ..OmniAnimations import OmniAnimations

"""
1. First user enters the object/objects they want to appear on the scene and what animation they 
want to happen (ex: rotate camera around the object)
2. Then call the s3 bucket with the corresponding object and load it into the omniverse scene - Done
3. Then pass in the corresponding omniverse template code into gpt along with the user
specified movement and generate a python script to do it
4. Put this script into Omniverse and animate the object
"""

def adding_python_scripts():
    output_str = ""
    output_str = parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/OmniAnimations.py", output_str)
    output_str = parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/Material.py", output_str)
    return output_str

def string_to_function_call(extension, func_string, prompt):
    # Extract function name and arguments

    match = re.match(r'(\w+)\((.*)\)', func_string)
    print("func_string: ", func_string)
    if not match:
        raise ValueError(f"Invalid function string format, match: {match}")
    
    func_name, args_string = match.groups()
    print("args_string: ", args_string)
    
    
    # Parse arguments
    kwargs = {}
    if args_string:
        end = args_string.find(')')
        args_string = args_string if end < 0 else args_string[:end+1]
        # Use ast.literal_eval to safely evaluate argument values
        parsed_args = [arg.strip() for arg in args_string.split(',')]
        for arg in parsed_args:
            if '=' in arg:
                key, value = arg.split('=')
                kwargs[key.strip()] = ast.literal_eval(value.strip())
    func = getattr(OmniAnimations, func_name)
    if not func:
        raise ValueError(f"Function '{func_name}' not found")
    
    # Call the function
    return func(extension, **kwargs)


def parsing_python_scripts(file_path, output_str):
    with open(file_path, 'r') as file:
        content = file.read()

    pattern = r'^\s*def\s+\w+\s*\([^)]*\)\s*(?:->\s*\w+)?\s*:\s*(?:"""[\s\S]*?""")?'
    matches = re.findall(pattern, content, re.MULTILINE)

    for match in matches:
        output_str += match + "\n\n"
    return output_str