import boto3
import os
import re
import json
from pxr import UsdGeom, Usd, Sdf
import omni.usd
import ast

from ..utils import get_extension_path
from ..UsdMethods.CameraAnimation import camera_zoom_in, camera_zoom_out, camera_pull_in, camera_push_out, camera_pan, camera_roll
"""
1. First user enters the object/objects they want to appear on the scene and what animation they 
want to happen (ex: rotate camera around the object)
2. Then call the s3 bucket with the corresponding object and load it into the omniverse scene - Done
3. Then pass in the corresponding omniverse template code into gpt along with the user
specified movement and generate a python script to do it
4. Put this script into Omniverse and animate the object
"""
def test():
    print("hello")

def processing_gpt_calls(prompt):
    from ..UsdMethods.GPTCalls import get_code_from_gpt

    with open("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/ParsedCode.txt", 'r') as file:
        content = file.read()
    code = get_code_from_gpt(prompt, content)
    return code 

def adding_python_scripts(txt_file_path: str):
    parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/Camera.py", txt_file_path)

    parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/Transform.py", txt_file_path)

    parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/Animation.py", txt_file_path)

    parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/CameraAnimation.py", txt_file_path)

    parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/CreateGeometry.py", txt_file_path)

    parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/Select.py", txt_file_path)

    parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/Material.py", txt_file_path)

def string_to_function_call(func_string, prompt):
    # Extract function name and arguments
    match = re.match(r'(\w+)\((.*)\)', func_string)
    if not match:
        raise ValueError("Invalid function string format")
    
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
                    print("in else statement appending prompt path")
                    args.append(f"/New_Stage/{prompt}")
    print("args", args)
    print("kwargs", kwargs)
    # Get the function from globals()
    func = globals().get(func_name)
    if not func:
        raise ValueError(f"Function '{func_name}' not found")
    
    # Call the function
    return func(f"/New_Stage/{prompt}", *kwargs.values())

def import_asset(prompt) -> str:
    """
    Pull the object from the AWS bucket and load it into the scene
    Args:
        prompt (str): the object the user wants to load
    Return:
        str: the path of the object
    """
    aws_access_id = "AKIA4HMIAHI53YO5JHJG"
    aws_secret_access_id = "gDjGAN+Y9XiOiEpTRJyscym1MDYeT1D/6rWW5uy+"
    region_name = "us-west-1"

    s3 = boto3.client('s3', 
                  aws_access_key_id=aws_access_id,
                  aws_secret_access_key=aws_secret_access_id,
                  region_name=region_name)

    bucket_name = "omni3dvideo"

    object = prompt
    s3_path = f"{object}/{object}_002/Scan/Scan.usd"
    ext_path = get_extension_path()
    asset_folder = f"{ext_path}/downloads/{object}"
    os.makedirs(asset_folder, exist_ok=True)

    local_path = os.path.join(asset_folder, f"model.usd").replace("\\", "/")
    print(local_path)

    if os.path.exists(local_path):
        print(f"File already exists at {local_path}")
    else:
        s3.download_file(bucket_name, s3_path, local_path)
    
    #Start of creating a reference for the prim
    add_reference(local_path, prompt)

def add_reference(local_path, prompt):
    # Create new USD stage
    stage: Usd.Stage = omni.usd.get_context().get_stage()

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


def parsing_python_scripts(file_path, output_file):
    if not os.path.exists(file_path):
        print(f"Error: Input file '{file_path}' does not exist.")
        return

    with open(file_path, 'r') as file:
        content = file.read()

    # Pattern to match function definitions and their docstrings, even if docstring is missing
    pattern = r'^\s*def\s+\w+\s*\([^)]*\)\s*(?:->\s*\w+)?\s*:\s*(?:"""[\s\S]*?""")?'

    # Find all matches
    matches = re.findall(pattern, content, re.MULTILINE)

    # Check if output directory exists, if not, create it
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










