import boto3
import os
import re
import json
from pxr import UsdGeom, Usd, Sdf
import ast

# from ..UsdMethods.CameraAnimation import camera_zoom_in, camera_zoom_out, camera_pull_in, camera_push_out, camera_pan, camera_roll
from ..UsdMethods.Material import apply_texture_from_file
from ..UsdMethods.CreateGeometry import place_object_on_another_object

from ..OmniAnimations import OmniAnimations

"""
1. First user enters the object/objects they want to appear on the scene and what animation they 
want to happen (ex: rotate camera around the object)
2. Then call the s3 bucket with the corresponding object and load it into the omniverse scene - Done
3. Then pass in the corresponding omniverse template code into gpt along with the user
specified movement and generate a python script to do it
4. Put this script into Omniverse and animate the object
"""
# def test():
#     print("hello")

# def processing_gpt_calls(prompt):
#     from ..UsdMethods.GPTCalls import get_code_from_gpt

#     with open("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/ParsedCode.txt", 'r') as file:
#         content = file.read()
#     code = get_code_from_gpt(prompt, content)
#     return code 

def adding_python_scripts(txt_file_path: str):
    # parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/Camera.py", txt_file_path)
    # parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/Transform.py", txt_file_path)
    # parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/Animation.py", txt_file_path)
    parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/OmniAnimations.py", txt_file_path)
    # parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/CreateGeometry.py", txt_file_path)
    # parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/Select.py", txt_file_path)
    parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/Material.py", txt_file_path)

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
        print("parsed_args: ", parsed_args)
        for arg in parsed_args:
            if '=' in arg:
                print("arg: ", arg)
                key, value = arg.split('=')
                print("key", key)
                print("value", value)
                kwargs[key.strip()] = ast.literal_eval(value.strip())

    print("kwargs", kwargs)
    # Get the function from globals()
    print("func_name:", func_name)
    func = getattr(OmniAnimations, func_name)
    if not func:
        raise ValueError(f"Function '{func_name}' not found")
    
    # Call the function
    return func(extension, **kwargs)


def parsing_python_scripts(file_path, output_file):
    if not os.path.exists(file_path):
        print(f"Error: Input file '{file_path}' does not exist.")
        return

    with open(file_path, 'r') as file:
        content = file.read()

    pattern = r'^\s*def\s+\w+\s*\([^)]*\)\s*(?:->\s*\w+)?\s*:\s*(?:"""[\s\S]*?""")?'
    matches = re.findall(pattern, content, re.MULTILINE)
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Write matches to output file
    try:
        with open(output_file, 'a') as out_file:
            for match in matches:
                out_file.write(match + "\n\n")  # Add extra newline for separation
        print(f"Extracted {len(matches)} functions to {output_file}")
    except PermissionError:
        print(f"Error: Permission denied when trying to write to '{output_file}'.")
        print("Please check if you have write permissions or if the file is open in another program.")
    except Exception as e:
        print(f"Error writing to output file: {str(e)}")










