import asyncio
import omni.kit.app
import omni.kit.asset_converter
import json
import os

def enable_converter_extension():
    ext_manager = omni.kit.app.get_app().get_extension_manager()
    if not ext_manager.is_extension_enabled("omni.kit.asset_converter"):
        ext_manager.set_extension_enabled_immediate("omni.kit.asset_converter", True)
    
    # if not ext_manager.is_extension_enabled("omni.kit.usdz_export"):
    #     ext_manager.set_extension_enabled_immediate("omni.kit.usdz_export", True)
    
def progress_callback(current_step: int, total: int):
    # Show progress
    print(f"{current_step} of {total}")

async def convert(input_asset_path, output_asset_path):
    # context = omni.kit.asset_converter.AssetConverterContext()
    # context.keep_all_materials = True
    # context.merge_all_meshes = True
    convert_task_manager = omni.kit.asset_converter.get_instance()
    task = convert_task_manager.create_converter_task(input_asset_path, output_asset_path, progress_callback)
    success = await task.wait_until_finished()
    if not success:
        detailed_status_code = task.get_status()
        detailed_status_error_string = task.get_error_message()
        print(f"Conversion failed with error code {detailed_status_code}: {detailed_status_error_string}")
    
    print(f"Conversion finished with success {success} at {output_asset_path}")
    return success

async def convert_assets(profile_path: str):
    """
    Convert the assets listed in the json file
    """
    with open(profile_path, "r") as f:
        profile_data = json.load(f)

    print("profile_data", profile_data)
    for id, path in profile_data.items():
        print(f"Converting {id} to USD")
        input_path  = path
        output_path = os.path.splitext(input_path)[0] + ".usd"
        if os.path.exists(output_path):
            print(f"{output_path} already exists, skipping")
            continue
        await convert(input_path, output_path)

    await asyncio.sleep(1)


