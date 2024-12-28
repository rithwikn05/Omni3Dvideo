import omni.ext
import omni.ui as ui
from pxr import UsdGeom, Gf, Usd, Sdf
import logging
import omni.kit.pipapi
import os
import re
import json
import omni.usd

logger = logging.getLogger(__name__)

from .UsdMethods.Select import *

stage = None
camera = None
camera_xformable = None


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
        self.prompt = ""
        self.stage = omni.usd.get_context().get_stage()
        assert self.stage
        # Usd.Stage.CreateNew("Omni3DVideoStage.usd")
        # default_prim = UsdGeom.Xform.Define(self.stage, Sdf.Path("/New_Stage"))
        # self.stage.SetDefaultPrim(default_prim.GetPrim())

        self.camera_path = '/perspectivecamera'
        camera = self.stage.DefinePrim(self.camera_path, "Camera")
        assert camera

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
        from .UsdMethods.ReadObjectsToOmni import import_asset
        from .UsdMethods.Material import generate_texture
        print(self.prompt_field.model.get_value_as_string())
        import_asset(self.prompt_field.model.get_value_as_string())
        generate_texture("/New_Stage/army_tank")
       

    def convert(self):
        from .UsdMethods.Material import generate_texture, apply_texture_from_file
        apply_texture_from_file("/New_Stage/army_tank", "C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/downloads/army-tank/textures/cat_image_texture.png")

    def build_animation(self):
        import re
        curr_time = 0.0
        from .UsdMethods.ReadObjectsToOmni import processing_gpt_calls, parsing_python_scripts, adding_python_scripts, import_asset, string_to_function_call
        from .UsdMethods.CameraAnimation import camera_zoom_in, camera_zoom_out, camera_pull_in, camera_push_out, camera_pan, camera_roll
        
        adding_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/ParsedCode.txt")
        from .UsdMethods.GPTCalls import get_code_from_gpt
        code = processing_gpt_calls(self.prompt_field.model.get_value_as_string())
        print(code)
        
        print(code)
        pattern = r'(?:.*\n){1}[^:]*:\s*(.*?)\s*(?:\n|$)(?:.*\n)?[^:]*:\s*(.*?)\s*(?:\n|$)'
    
        match = re.search(pattern, code, re.DOTALL)
        if match:
            subject = match.group(1).strip()
            method = match.group(2).strip()

        print(subject)

        import_asset(self, subject)
        
        string_to_function_call(self, method, subject)

    def render_video(self):
        from .UsdMethods.CaptureVideo import render_video, setup_viewport
        output_path = "C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods"
        viewport_api, viewport_widget, viewport_window = setup_viewport()
        render_video(viewport_api, output_path)
        viewport_widget.destroy()
        viewport_window.destroy()
