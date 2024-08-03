import boto3
import os
import re
import ast

"""
1. First user enters the object/objects they want to appear on the scene and what animation they 
want to happen (ex: rotate camera around the object)
2. Then call the s3 bucket with the corresponding object and load it into the omniverse scene - Done
3. Then pass in the corresponding omniverse template code into gpt along with the user
specified movement and generate a python script to do it
4. Put this script into Omniverse and animate the object
"""

def processing_gpt_calls(prompt):
    from ..UsdMethods.GPTCalls import get_code_from_gpt

    with open("ParsedCode.txt", 'r') as file:
        content = file.read()
    code = get_code_from_gpt(prompt, content)
    return code 


def pulling_from_aws(prompt):
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
    local_path = "C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/Scan.usd"

    s3.download_file(bucket_name, s3_path, local_path)

def parsing_python_scripts(file_path, output_file):
    try:
        # Check if input file exists
        if not os.path.exists(file_path):
            print(f"Error: Input file '{file_path}' does not exist.")
            return

        with open(file_path, 'r') as file:
            content = file.read()

        # Pattern to match function definitions and their docstrings, even if docstring is missing
        pattern = (
            r'^\s*def\s+\w+\s*\([^)]*\)\s*->\s*\w+\s*:\s*"""\s*[\s\S]*?\s*"""'
        )


        # Find all matches
        matches = re.findall(pattern, content, re.MULTILINE)
        
        # Find all matches
        # matches = re.findall(pattern, content, re.MULTILINE)

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

        # Debug: print the first 500 characters of the file content
        print("\nFirst 500 characters of the file:")
        print(content[:500])

        # Debug: print the first few matches (if any)
        print("\nFirst few matches:")
        for match in matches[:3]:
            print(match)
            print("---")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/Camera.py", "C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/ParsedCode.txt")

parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/Transform.py", "C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/ParsedCode.txt")

parsing_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/Animation.py", "C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/ParsedCode.txt")

output = processing_gpt_calls("battery")
print(output)
# pulling_from_aws("rotate around battery.")









