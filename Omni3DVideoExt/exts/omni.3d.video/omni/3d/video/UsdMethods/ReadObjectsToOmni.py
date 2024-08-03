import boto3
import os


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

    local_path = os.path.join(asset_folder, f"model.usd")

    if os.path.exists(local_path):
        print(f"File already exists at {local_path}")
    else:
        s3.download_file(bucket_name, s3_path, local_path)


pulling_from_aws("battery")









