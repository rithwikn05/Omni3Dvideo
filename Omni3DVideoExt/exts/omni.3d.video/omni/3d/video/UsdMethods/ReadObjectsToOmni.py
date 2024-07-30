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

def processing_gpt_calls(self, prompt, omni_code):
    from .UsdMethods.GPTCalls import get_code_from_gpt

    code = get_code_from_gpt(prompt, omni_code)
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


pulling_from_aws("battery")









