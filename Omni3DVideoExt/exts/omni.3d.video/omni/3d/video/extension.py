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
        self.time = 0.0 #self.stage.GetStartTimeCode()#.GetValue()
        self.timeline = omni.timeline.get_timeline_interface()
        self.timeline.set_start_time(0.0)
        
        focal_length_attr = self.camera.GetAttribute("focalLength")
        current_focal_length = focal_length_attr.Get()
        new_focal_length = current_focal_length / 2
        print("new_focal_length: ", new_focal_length)
        focal_length_attr.Set(value=new_focal_length)

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
        from .UsdMethods.ReadObjectsToOmni import adding_python_scripts, string_to_function_call
        from .UsdMethods.GPTCalls import get_code_from_gpt

        content = adding_python_scripts()

        gpt_output = get_code_from_gpt(self.prompt_field.model.get_value_as_string(), content)
        print("GPT Output: ", gpt_output)
        
        mode = None
        actions = []
        subjects = []
        methods = []
        mode = None
            
        #Reset the xformable order
        self.camera_xformable.SetXformOpOrder([])

        self.translateOp = self.camera_xformable.AddTranslateOp()
        initial_translation = Gf.Vec3d(0, 100, 500)
        self.translateOp.Set(initial_translation)

        self.rotateXYZOp = self.camera_xformable.AddRotateXYZOp()
        initial_rotation = Gf.Vec3d(0.0, 0.0, 0.0)
        self.rotateXYZOp.Set(initial_rotation)
        

        for line in gpt_output.split("\n"):
            if "Action" in line: mode = "action"
            elif "Subject" in line: mode = "subject"
            elif "Method" in line: mode = "method"
            elif mode == "action": actions.append(line.split()[1].lower())
            elif mode == "subject": subjects.append(line.split()[1].lower())
            elif mode == "method": methods.append(line[3:].lower()) 
            # print("line: ", line)
        print("subjects: ", subjects)
        print("methods: ", methods)

        # subjects = ["armchair", "alarm-clock"]
        # methods = ["camera_pull_in(pull_distance=100, duration=20)", "camera_push_out(push_distance=100, duration=20)"]
        # methods = ["camera_zoom_in(zoom_ratio=5, duration=10)", "camera_zoom_out(zoom_ratio=5, duration=10)"]
        # methods = ["camera_pull_in(pull_distance=100, duration=20)", "camera_push_up(pull_distance=50, duration=20)"]
        # methods = ["camera_pull_in(pull_distance=100, duration=20)", "camera_push_up(pull_distance=50, duration=20)",
        #            "prim_translate(direction='up', prim_path = '/New_Stage/armchair', distance=100, duration=20, start=10)",
        #            "prim_roll(rotation_axis = 'Z', prim_path = '/New_Stage/armchair', roll_angle = 360, duration=10)"]
        
        # prompt: Import armchair. Import alarm-clock. Pull into an armchair by 300 units for 4 seconds. Make the alarm clock rotate along by 360 degrees for 4 seconds and start after 0 seconds. Push up from an armchair by 500 units for 4 seconds. Translate the armchair up 500 units for 4 seconds and start after 4 seconds. Place a light called MrLight with intensity of 1000 with color blue pointing at armchair. Place background around armchair with pink.

        #Import armchair. Import alarm-clock. Pull the camera closer by 500 units for 4 seconds, starting after 0 seconds. Use the camera to zoom in by a factor of 1.5 for 3 seconds, starting after 4 seconds. Push the camera upward by 400 units for 5 seconds, starting after 11 seconds.

        print("Stage start time code ", self.stage.GetStartTimeCode())
        print("USD Earliest Time", math.isnan(Usd.TimeCode.EarliestTime().GetValue()))

        if subjects and methods:
            print("zip(subjects, methods): ", zip(subjects, methods))
            for match in zip(subjects, methods):
                print("self.time: ", self.time)
                subject = match[0].strip()
                method = match[1].strip()

                print(f"Processing Subject: {subject}, Method: {method}")
                
                print("subject: ", subject)
                string_to_function_call(self, method, subject)
        else:
            print("[WARNING] something went wrong, could not parse GPT response") # TODO: promote to error status?
        
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
