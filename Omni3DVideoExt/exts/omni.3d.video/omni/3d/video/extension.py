from .Omni3DVideo import Omni3DVideo
from .UsdMethods.GPTCalls import GPTCoder

from .UsdMethods.ReadObjectsToOmni import processing_gpt_calls, parsing_python_scripts, adding_python_scripts, import_asset, string_to_function_call
from .UsdMethods.CameraAnimation import camera_zoom_in, camera_zoom_out, camera_pull_in, camera_push_out, camera_pan, camera_roll

from .UsdMethods.ReadObjectsToOmni import import_asset
from .UsdMethods.Material import generate_texture

from .UsdMethods.Material import generate_texture, apply_texture_from_file

from .UsdMethods.Select import *

import omni.ext
import omni.ui as ui

from pxr import UsdGeom, Gf, Usd, Sdf

import logging
import omni.kit.pipapi
import os
import re
import json

logger = logging.getLogger(__name__)

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

        # stage creation
        self.stage = Usd.Stage.CreateNew("Omni3DVideoStage.usd") # TODO: decide whether responsibility for creating stage should be here, or in Omni3dVideo

        self.prompt_field = "" # ui thing # TODO: maybe dont initialize with "" because it's a bit confusing, eventually it will be a ui.StringField, which isn't the same type of object
        self.prompt = "" # string that actually holds the prompt


        self.omni3dvideo = Omni3DVideo() # backend animation stuff

        os.environ["OPENAI_API_KEY"] = "sk-XFbm9kZEDffLd85VzKTAdAqPRV-AOtLJQpeX4Xi_KHT3BlbkFJYW9yCcTjbd0TCLhaWCvU9hYD4r5t6UHuFi_S4gt8wA" # TODO: remove later, security risk
        self.gpt_coder = GPTCoder()

    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[omni.3d.video] omni 3d video startup")

        self._count = 0

        self._window = ui.Window("Omni3DVideo Debug Window", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                def _generate():
                    self.prompt = self.prompt_field.name
                    print(self.prompt)

                label = ui.Label("Debug Window", height = 20)
                with ui.HStack(height = ui.Percent(20)):
                    ui.Label("Prompt", width = 70)
                    self.prompt_field = ui.StringField(multiline = True)    
                    self.prompt = self.prompt_field.model.get_value_as_string()
                # ui.Button("debug", height = 20, clicked_fn=self.debug)
                ui.Button("read prompt", height = 20, clicked_fn=_generate)
                ui.Button("debug2", height = 20, clicked_fn=self.debug2)
                ui.Button("convert", height = 20, clicked_fn=self.convert)
                ui.Button("build_animation", height = 20, clicked_fn=self.build_animation)
                ui.Button("Render Video", height = 20, clicked_fn=self.render_video)

   
    def debug2(self):
        print(self.prompt_field.model.get_value_as_string())
        import_asset(self.prompt_field.model.get_value_as_string())
        generate_texture("/New_Stage/army_tank") # TODO: WARNING: this is currently hardcoded to be army_tank!

    # TODO: fix this method or delete it 
    def convert(self):
        apply_texture_from_file("/New_Stage/army_tank", "C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/downloads/army-tank/textures/cat_image_texture.png")

    def build_animation(self):
        curr_time = 0.0 # TODO: WARNING: unused local variable
        self.camera_xformable.SetXformOpOrder([]) # TODO: WARNING, these don't exist anymore!!!
        self.camera_xformable.AddRotateXYZOp()
        self.camera_xformable.AddTranslateOp()
        
        # initializing ParsedCode.txt! 
        # TODO: does this need to be done once per extension loadup, or does it need to be done every time build animation is called? 
        # if its the former, plz move this line to on_startup or __init__
        adding_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/ParsedCode.txt")
        
        # work with GPTCoder
        with open("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/ParsedCode.txt", 'r') as file:
            content = file.read() # TODO: You do realize lol, you just wrote this content to the file on the previous line... and now you're immediately reading it back. there was no point in storing it in the file in the first place, just return the string from the grab_python_scripts method. OR, take that string and store it somewhere in memory (either RAM or file system) and use it directly, rather than do all this funny business.
        code = self.gpt_coder.get_code(self.prompt_field.model.get_value_as_string(), content)
        print(code)
        
        print(code)
        pattern = r'(?:.*\n){1}[^:]*:\s*(.*?)\s*(?:\n|$)(?:.*\n)?[^:]*:\s*(.*?)\s*(?:\n|$)' # TODO: comment what this does
    
        match = re.search(pattern, code, re.DOTALL)
        if match:
            subject = match.group(1).strip()
            method = match.group(2).strip()

            print(subject)

            import_asset(stage, subject)
            string_to_function_call(stage, camera, method, subject)

            # TODO: multi-step animations: will something like this work?
            subjects = ...
            methods = ...
            for subject in subjects:
                import_asset(stage, subject)
            for idx, method in enumerate(methods):
                string_to_function_call(stage, camera, method, subjects[idx])
        else:
            print("[WARNING] Something went wrong, could not parse GPT response") # TODO: promote to error status?

    def render_video(self):
        from .UsdMethods.CaptureVideo import render_video, setup_viewport
        output_path = "C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods"
        viewport_api, viewport_widget, viewport_window = setup_viewport()
        render_video(viewport_api, output_path)
        viewport_widget.destroy()
        viewport_window.destroy()
