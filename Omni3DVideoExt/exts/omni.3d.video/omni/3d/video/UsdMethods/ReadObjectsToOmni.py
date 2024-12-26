# TODO: severe coding malpractice to refer to files in the previous directory, ur directory structure should be better planned
from ..utils import get_extension_path
# from ..UsdMethods.CameraAnimation import camera_zoom_in, camera_zoom_out, camera_pull_in, camera_push_out, camera_pan, camera_roll
from ..UsdMethods.Material import apply_texture_from_file
from ..UsdMethods.CreateGeometry import place_object_on_another_object

from ..Omni3DVideo import Omni3DVideo

import boto3

from pxr import UsdGeom, Usd, Sdf
import omni.usd

import os
import re
import json
import ast

"""
1. First user enters the object/objects they want to appear on the scene and what animation they 
want to happen (ex: rotate camera around the object)
2. Then call the s3 bucket with the corresponding object and load it into the omniverse scene - Done
3. Then pass in the corresponding omniverse template code into gpt along with the user
specified movement and generate a python script to do it
4. Put this script into Omniverse and animate the object
"""

# TODO: commented for deletion
# def test():
#     print("hello")

# TODO: commented for deletion
# def processing_gpt_calls(prompt): # TODO: ermmmmm... this is a wrapper for your own python method from another file!
#     from ..UsdMethods.GPTCalls import get_code_from_gpt

#     with open("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/ParsedCode.txt", 'r') as file:
#         content = file.read()
#     code = get_code_from_gpt(prompt, content)
#     return code 

# TODO: what exactly does this do, is it mainly all the animation methods?
def adding_python_scripts(txt_file_path: str):
    parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/Camera.py", txt_file_path)
    parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/Transform.py", txt_file_path)
    parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/Animation.py", txt_file_path)
    parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/CameraAnimation.py", txt_file_path)
    parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/CreateGeometry.py", txt_file_path)
    parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/Select.py", txt_file_path)
    parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/Material.py", txt_file_path)

def string_to_function_call(stage, camera, func_string, prompt):
    # Extract function name and arguments

    match = re.match(r'(\w+)\((.*)\)', func_string)
    if not match:
        raise ValueError(f"Invalid function string format, match: {match}")
    
    func_name, args_string = match.groups()
    
    # Parse arguments
    args = []
    kwargs = {}
    if args_string:
        # Use ast.literal_eval to safely evaluate argument values
        parsed_args = [arg.strip() for arg in args_string.split(',')]
        print(parsed_args)
        for arg in parsed_args:
            if '=' in arg:
                key, value = arg.split('=')
                print("key", key)
                print("value", value)
                kwargs[key.strip()] = ast.literal_eval(value.strip())
            else:
                if args == "camera_path: str":
                    print(f"/New_Stage/{prompt}")
                    args.append(f"/New_Stage/{prompt}")
    
    print("args", args)
    print("kwargs", kwargs)
    # Get the function from globals()
    func = getattr(Omni3DVideo, func_name)
    if not func:
        raise ValueError(f"Function '{func_name}' not found")
    
    # Call the function
    return func(stage, camera, *kwargs.values())

def import_asset(stage, prompt) -> str:
    """
    Pull the object from the AWS bucket and load it into the scene
    Args:
        prompt (str): the object the user wants to load
    Return:
        str: the path of the object
    """
    aws_access_id = "AKIA4HMIAHI53YO5JHJG" # TODO: MAGIC VALUE!
    aws_secret_access_id = "gDjGAN+Y9XiOiEpTRJyscym1MDYeT1D/6rWW5uy+" # TODO: MAGIC VALUE!
    region_name = "us-west-1" # TODO: MAGIC VALUE!
    # TODO: to avoid this, there are two solutions:
    # 1. create an encapsulation/class for this data, and have a method in that class called import_asset
    # 2. require users to pass in this data every time import_asset is called
    # the former might be better if AWS buckets can be "kept open" to reduce latency when this method is called multiple times in succession

    s3 = boto3.client('s3', 
                  aws_access_key_id=aws_access_id,
                  aws_secret_access_key=aws_secret_access_id,
                  region_name=region_name)

    bucket_name = "omni3dvideo"
    prefix = f"Assets/{prompt}"
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    if 'Contents' not in response:
        print(f"No objects found with prefix '{prefix}'")

    for obj in response['Contents']:
        # Print or return the full S3 URL
        object_key = obj['Key']
        s3_url = f"s3://{bucket_name}/{object_key}"
        break

    s3_object_path = s3_url[len("s3://omni3dvideo/"):]
    print("s3_object_path", s3_object_path)

    pattern = r"(\w+(?:-\w+)?)/([0-9a-f]+)/model\.usd"
    match = re.search(pattern, s3_object_path)
    print("match", match)
    if match:
        prompt = match.group(1)
        hash_value = match.group(2)
        print(f"Prompt: {prompt}")
        print(f"Hash: {hash_value}")
    else:
        print("No match found")

    # New code to dynamically determine texture path
    def get_texture_path_from_s3(bucket_name, base_path):
        texture_prefix = f"{base_path}textures/"
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=texture_prefix)
        
        for obj in response.get('Contents', []):
            if obj['Key'].endswith(('_texture0.png', '_texture0.jpg')):
                return obj['Key']
        return None
    
    base_path = f"Assets/{prompt}/{hash_value}/"
    s3_texture_path = get_texture_path_from_s3(bucket_name, base_path)
    print("s3_texture_path", s3_texture_path)

    def sanitize_for_filesystem(name: str) -> str:
        # Replace spaces with hyphens, remove other invalid characters
        return re.sub(r'[^a-zA-Z0-9-]', '-', name.replace(' ', '-')).lower()

    def sanitize_for_usd(name: str) -> str:
        # Replace spaces and hyphens with underscores, remove other invalid characters
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name.replace('-', '_').replace(' ', '_'))
        # Ensure the name starts with a letter or underscore
        if not sanitized[0].isalpha() and sanitized[0] != '_':
            sanitized = '_' + sanitized
        return sanitized

    filesystem_prompt = sanitize_for_filesystem(prompt)
    usd_prompt = sanitize_for_usd(prompt)
        
    ext_path = get_extension_path()
    object_asset_folder = f"{ext_path}/downloads/{filesystem_prompt}/models/"
    texture_asset_folder = f"{ext_path}/downloads/{filesystem_prompt}/textures/"    
    os.makedirs(object_asset_folder, exist_ok=True) 
    os.makedirs(texture_asset_folder, exist_ok=True)

    local_object_path = os.path.join(object_asset_folder, f"model.usd").replace("\\", "/")
    if s3_texture_path:
        local_texture_path = os.path.join(texture_asset_folder, os.path.basename(s3_texture_path)).replace("\\", "/")


    if os.path.exists(local_object_path):
        print(f"File already exists at {local_object_path}")
    else:
        print("downloaded")
        s3.download_file(bucket_name, s3_object_path, local_object_path)
    
    if s3_texture_path:
        if os.path.exists(local_texture_path):
            print(f"File already exists at {local_texture_path}")
        else:
            print("second download")
            s3.download_file(bucket_name, s3_texture_path, str(local_texture_path))

    #Start of creating a reference for the prim
    add_reference(stage, local_object_path, usd_prompt)
    if s3_texture_path:
        apply_texture_from_file(f"/New_Stage/{usd_prompt}", local_texture_path)

def add_reference(stage, local_path, prompt):

    print("in add reference")

    # Create and define default prim, so this file can be easily referenced again
    default_prim = UsdGeom.Xform.Define(stage, Sdf.Path("/New_Stage"))
    stage.SetDefaultPrim(default_prim.GetPrim())

    # Create an xform which should hold all references
    ref_prim: Usd.Prim = UsdGeom.Xform.Define(stage, Sdf.Path(f"/New_Stage/{prompt}")).GetPrim()

    # Add an external reference to the local_path USD file
    add_ext_reference(ref_prim, local_path, Sdf.Path.emptyPath)

    # Export the stage to a string and print it
    usda = stage.GetRootLayer().ExportToString()
    print(usda)

    # Get a list of all prepended references
    references = []
    for prim_spec in ref_prim.GetPrimStack():
        references.extend(prim_spec.referenceList.prependedItems)

    # Check that the reference prim was created and that the references are correct
    assert ref_prim.IsValid()
    assert references[0] == Sdf.Reference(assetPath=local_path)

def add_int_reference(prim: Usd.Prim, ref_target_path: Sdf.Path) -> None:
        references: Usd.References = prim.GetReferences()
        references.AddInternalReference(ref_target_path)

def add_ext_reference(prim: Usd.Prim, ref_asset_path: str, ref_target_path: Sdf.Path) -> None:
        references: Usd.References = prim.GetReferences()
        references.AddReference(
            assetPath=ref_asset_path,
            primPath=ref_target_path # OPTIONAL: Reference a specific target prim. Otherwise, uses the referenced layer's defaultPrim.
        )


# TODO: comment this method better, figure out what it does
def parsing_python_scripts(file_path, output_file):
    if not os.path.exists(file_path):
        print(f"Error: Input file '{file_path}' does not exist.")
        return

    with open(file_path, 'r') as file:
        content = file.read()

    pattern = r'^\s*def\s+\w+\s*\([^)]*\)\s*(?:->\s*\w+)?\s*:\s*(?:"""[\s\S]*?""")?' # TODO: ermmmm... what does this regex do, add comment
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










