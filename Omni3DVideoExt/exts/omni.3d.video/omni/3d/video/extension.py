import omni.ext
import omni.ui as ui
from pxr import UsdGeom
import logging
import omni.kit.pipapi
# from openai import OpenAI
import os
import re
import json
# import openai

logger = logging.getLogger(__name__)

from .UsdMethods.Select import *


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class Omni3dVideoExtension(omni.ext.IExt):

    try:
        from typing_extensions import override
    except (ImportError, AttributeError):
        def override(f):
            return f

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.prompt_field = ""

    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[omni.3d.video] omni 3d video startup")

        self._count = 0

        self._window = ui.Window("Omni3DVideo Debug Window", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                label = ui.Label("Debug Window", height = 20)
                with ui.HStack(height = ui.Percent(20)):
                    ui.Label("Prompt", width = 70)
                    self.prompt_field = ui.StringField(multiline = True)
                # ui.Button("debug", height = 20, clicked_fn=self.debug)
                ui.Button("debug2", height = 20, clicked_fn=self.debug2)
                # ui.Button("convert", height = 20, clicked_fn=self.convert)
                ui.Button("generate", height = 20, clicked_fn=self.run_gpt_generated_code)

    def on_shutdown(self):
        print("[omni.3d.video] omni 3d video shutdown")

    def debug(self):
        # from .UsdMethods.CreateAssets import createAssets
        # from .UsdMethods.Transform import transform
        # from .UsdMethods.Camera import camera
        
        # #Create shapes
        # createasset = createAssets()
        # cube = createasset.create_cube("/a_cube")
        # sphere = createasset.create_sphere("/a_sphere")

        # #The order in which you apply the transformations changes where the object ends up

        # #transform objects
        # transformObj = transform()
        # #cube
        # xformableCube = UsdGeom.Xformable(cube)
        # xformableCube.SetXformOpOrder([])
        # transformObj.translate(xformableCube, (10.0, 15.0, 15.0))
        # transformObj.orient(xformableCube)
        # transformObj.scale(xformableCube, (75, 75, 75))
        # transformObj.rotate(xformableCube, (0, 1, 0))

        # #sphere
        # xformableSphere = UsdGeom.Xformable(sphere)
        # xformableSphere.SetXformOpOrder([])
        # transformObj.scale(xformableSphere, (75, 75, 75))
        # transformObj.rotate(xformableSphere, (0, 1, 0))
        # transformObj.translate(xformableSphere, (10.0, 15.0, 15.0))

        # #Modifying Camera
        # cameraObj = camera()
        # cameras = cameraObj.getCameraPrim()
        # xformableSphere.SetXformOpOrder([])
        # cameraObj.setFocalLength(cameras, 15.0)
        # cameraObj.setHorizAperature(cameras, 36.0)
        # cameraObj.setVertAperature(cameras, 24.0)
        # cameraObj.setClippingRange(cameras, (0.1, 1000.0))

        # #translate camera
        # xformableCamera = UsdGeom.Xformable(cameras)
        # xformableCamera.SetXformOpOrder([])
        # transformObj.translate(xformableCamera, (100.0, 200.0, 500.0))
        # transformObj.rotate(xformableCamera, (0, 1, 0))
        # transformObj.scale(xformableCamera, (2, 2, 2))
        # print("Hello")


        def select_and_hide_cube() -> None:
            """
            Select and hide the prim at the path "/World/Cube".
            """
            prim_path = ["/World/Cube"]
            select_prims(prim_path)
            hide_selected_prims()

        select_and_hide_cube() 

    def debug2(self):
        # print("debug2")

        # from .utils import get_extension_path
        # logger.info(get_extension_path())

        # from .UsdMethods.Material import generate_texture
        # generate_texture("/World/Cube", "A chubby orange cat riding through space, digital art")
        
        # from .UsdMethods.Camera import create_camera_look_at
        # create_camera_look_at("/World/Cube")

        from .UsdMethods.Animation import keyframe, create_movement_animation, create_rotation_animation, create_scale_animation

        keyframe("/World/Cube", "/World/Cube.xformOp:translate|x", 5.0, 50.0)
        # keyframe("/World/Cube", "/World/Cube.xformOp:translate|x", 100.0, 100.0)

        # create_scale_animation("/World/Cube", 500, 2.0)
        # print(self.prompt_field.name)

        # from .UsdMethods.ReadObjectsToOmni import import_asset
        # import_asset("battery")
        
    def convert(self):
        from .UsdMethods.ConvertToUSD import convert

        import asyncio

        asyncio.ensure_future(convert("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/anise_001_scan.obj", 
                                      "C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/anise_001_scan_usd.usd"))
        

        
    def run_gpt_generated_code(self):
        from .UsdMethods.ReadObjectsToOmni import import_asset, read_parsed_code
        from .UsdMethods.GPTCalls import get_code_from_gpt
        import_asset("battery")
        omniverse_code = read_parsed_code("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/ParsedCode.txt")
        code = get_code_from_gpt("battery", omniverse_code)
        # print(code)
    