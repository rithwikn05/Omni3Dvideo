import omni.ext
import omni.ui as ui
from pxr import UsdGeom, Gf, Usd, Sdf
import logging
import omni.kit.pipapi
import os
import re
import json
import omni.usd
import omni.timeline
import math

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
        self.camera = self.stage.DefinePrim(self.camera_path, "Camera")
        self.camera_xformable = UsdGeom.Xformable(self.camera)
        # camera_xformable = camera_xformable.AddTranslateOp()
        # camera_xformable = camera_xformable.AddRotateXYZOp()
        
        assert self.camera
        self.time = 0.0#self.stage.GetStartTimeCode()#.GetValue()
        self.timeline = omni.timeline.get_timeline_interface()
        self.timeline.set_start_time(0.0)

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
        from .UsdMethods.ReadObjectsToOmni import adding_python_scripts, import_asset, string_to_function_call
        from .UsdMethods.GPTCalls import get_code_from_gpt

        adding_python_scripts("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/ParsedCode.txt")

        with open("C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods/ParsedCode.txt", 'r') as file:
            content = file.read() # TODO: You do realize lol, you just wrote this content to the file on the previous line... and now you're immediately reading it back. there was no point in storing it in the file in the first place, just return the string from the grab_python_scripts method. OR, take that string and store it somewhere in memory (either RAM or file system) and use it directly, rather than do all this funny business.
        # gpt_output = get_code_from_gpt(self.prompt_field.model.get_value_as_string(), content)
        # print("GPT Output: ", gpt_output)
        
        # pattern = r'\d+\.\s*(.*?)\s*\(.*?\)\s*.*?Methods:\s*[\s\S]*?\d+\.\s*([a-zA-Z_]+)'
        # #r'(?:.*\n){1}[^:]*:\s*(.*?)\s*(?:\n|$)(?:.*\n)?[^:]*:\s*(.*?)\s*(?:\n|$)'
        # subject_pattern = r'Subjects:\s*(?:\d+\.\s*(.*?)(?:\s*\(.*?\))?\s*)+'
        # method_pattern = r'Methods:\s*(?:\d+\.\s*([a-zA-Z_]+)\(.*?\)\s*)+'
    
        # subejct_matches = re.findall(r'\d+\.\s*(.*?)(?:\s*\(.*?\))?', re.search(subject_pattern, gpt_output))
        # method_matches = re.findall(r'\d+\.\s*([a-zA-Z_]+)\(.*?\)', re.search(method_pattern, gpt_output))
        # print("subejct_matches: ", subejct_matches)
        # print("method_matches: ", method_matches)

        
        mode = None
        actions = []
        subjects = []
        methods = []
        mode = None

        #Reset the xformable order
        self.camera_xformable.SetXformOpOrder([])

        self.translateOp = self.camera_xformable.AddTranslateOp()
        initial_translation = Gf.Vec3d(0, 100, 1000)
        self.translateOp.Set(initial_translation)

        self.rotateXYZOp = self.camera_xformable.AddRotateXYZOp()
        initial_rotation = Gf.Vec3d(0.0, 0.0, 0.0)
        self.rotateXYZOp.Set(initial_rotation)
        

        # for line in gpt_output.split("\n"):
        #     if "Action" in line: mode = "action"
        #     elif "Subject" in line: mode = "subject"
        #     elif "Method" in line: mode = "method"
        #     elif mode == "action": actions.append(line.split()[1].lower())
        #     elif mode == "subject": subjects.append(line.split()[1].lower())
        #     elif mode == "method": methods.append(line[3:].lower()) 
        #     # print("line: ", line)
        # print("subjects: ", subjects)
        # print("methods: ", methods)

        subjects = ["armchair", "armchair", "armchair", "armchair"]
        # methods = ["camera_pull_in(pull_distance=100, duration=20)", "camera_push_out(push_distance=100, duration=20)"]
        # methods = ["camera_zoom_in(zoom_ratio=5, duration=10)", "camera_zoom_out(zoom_ratio=5, duration=10)"]
        # methods = ["camera_pull_in(pull_distance=100, duration=20)", "camera_push_up(pull_distance=50, duration=20)"]
        methods = ["camera_pull_in(pull_distance=100, duration=20)", "camera_push_up(pull_distance=50, duration=20)",
                   "prim_translate(direction='up', prim_path = '/New_Stage/armchair', distance=100, duration=20)",
                   "prim_roll(rotation_axis = 'Z', prim_path = '/New_Stage/armchair', roll_angle = 360, duration=10)"]
        # Translate a soda-can up 100 units for 10 seconds. Rotate a soda-can by 360 degrees for 10 seconds. Zoom into the soda can by 100 units for 10 seconds.

        print("Stage start time code ", self.stage.GetStartTimeCode())
        print("USD Earliest Time", math.isnan(Usd.TimeCode.EarliestTime().GetValue()))

        if subjects and methods:
            # print(matches)

            print("zip(subjects, methods): ", zip(subjects, methods))
            for match in zip(subjects, methods):
                print("self.time: ", self.time)
                subject = match[0].strip()
                method = match[1].strip()

                print(f"Processing Subject: {subject}, Method: {method}")

                # Replace with your function calls
                import_asset(self, subject)
                string_to_function_call(self, method, subject)
        else:
            print("[WARNING] Something went wrong, could not parse GPT response") # TODO: promote to error status?
        
        self.timeline.set_end_time(70)
        self.time = 0
        self.timeline.set_start_time(0.0)

    def render_video(self):
        from .UsdMethods.CaptureVideo import render_video, setup_viewport
        output_path = "C:/OmniUSDResearch/Omni3DVideoExt/exts/omni.3d.video/omni/3d/video/UsdMethods"
        viewport_api, viewport_widget, viewport_window = setup_viewport()
        render_video(viewport_api, output_path)
        viewport_widget.destroy()
        viewport_window.destroy()
