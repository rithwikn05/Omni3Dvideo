from pxr import UsdGeom, Usd, Gf, Sdf, UsdLux, UsdShade
import omni.usd, omni.timeline
from omni.timeline import get_timeline_interface
import math
import numpy as np
import boto3
import re
import os
from .utils import get_extension_path
from .UsdMethods.Material import apply_texture_from_file
from .UsdMethods.CreateGeometry import place_object_on_another_object

class OmniAnimations():
    #######################################################
    #               Camera Animation Methods              #
    #######################################################

    # def create_camera_rotate_around_object_animation(stage, camera, prim_path: str, duration: float, angle: float = 45, distance: float = 200) -> None:
    #     """
    #     Create a camera animation that rotates around an object
    #     """
    #     prim = stage.DefinePrim(prim_path, "Cube")

    #     timeline = get_timeline_interface()

    #     translate_op = camera_xformable.AddTranslateOp()
    #     orient_op = camera_xformable.AddOrientOp()

    #     # angle_in_radians = math.radians(angle) - math.radians(angle) * 2

    #     # matrix: Gf.Matrix4d = omni.usd.get_world_transform_matrix(prim)
    #     target_prim_xform_mat = UsdGeom.Xformable(prim).GetLocalTransformation()
    #     translate = target_prim_xform_mat.ExtractTranslation()
    #     print(translate)

    #     # z_dist = distance * math.cos(angle_in_radians)
    #     # y_dist = distance * math.sin(angle_in_radians)
    #     # translation_position = Gf.Vec3f(translate[0], translate[1] - y_dist, translate[2] + z_dist)

    #     frames_per_second = timeline.get_time_codes_per_seconds()
    #     start_time = timeline.get_start_time()
    #     end = start_time + (duration * frames_per_second)

    #     # new_translation = translation_position
    #     up_direction = Gf.Vec3d(0, 1, 0)
    #     timeline.pause()

    #     for current_time in np.arange(start_time, end, 1/frames_per_second):#int(start_time * frames_per_second), int(end * frames_per_second)):
    #         rotation_angle_radians = math.radians(angle * ((current_time - start_time) / duration))

    #         new_z_dist = distance * math.cos(rotation_angle_radians)      
    #         new_y_dist = distance * math.sin(rotation_angle_radians)

    #         new_translation = Gf.Vec3d(translate[0], translate[1] + new_y_dist, translate[2] + new_z_dist)
    #         print(new_translation)
    #         # print(up_direction)
    #         # new_rotation = Gf.Quatf(math.cos(rotation_angle_radians / 2), axis[0] * math.sin(rotation_angle_radians / 2), axis[1] * math.sin(rotation_angle_radians / 2), axis[2] * math.sin(rotation_angle_radians / 2))
            
    #         look_at = Gf.Matrix4d(1.0)
    #         print(look_at)
    #         look_at = look_at.SetLookAt(new_translation, translate, up_direction)       
    #         new_rotation = look_at.ExtractRotation().GetQuat()
    #         new_rotation = Gf.Quatf(new_rotation)

    #         timeline.set_current_time(current_time)

    #         translate_op.Set(new_translation)
    #         orient_op.Set(new_rotation)
            
    #     timeline.set_auto_update(True)
    #     timeline.set_start_time(start_time)
    #     timeline.set_end_time(end)

    def camera_zoom_in(extension, zoom_ratio: float = 2.0, duration: float = 3, start: float = None):
        """
        Create a camera zoom in animation

        Args:
            zoom_ratio (float): the ratio of the zoom
            duration (float): the duration of the animation in seoconds
            start (float): the start time of the animation in seconds
        """
        print("In camera_zoom_in function")
        # stage = omni.usd.get_context().get_stage()
        camera = extension.stage.GetPrimAtPath(extension.camera_path)
        focal_length_attr = camera.GetAttribute("focalLength")
        current_focal_length = focal_length_attr.Get()
        new_focal_length = current_focal_length * zoom_ratio

        print("initial extension.time: ", extension.time)
        focal_length_attr.Set(value=current_focal_length, time=start if start != None else extension.time)
        extension.timeline.set_start_time(start if start != None else extension.time) # TODO: wait, I don't think we want to do this yet.
        if start == None: extension.time += duration * extension.stage.GetFramesPerSecond()
        
        focal_length_attr.Set(value=new_focal_length, time=start+duration if start != None else extension.time)
        extension.timeline.set_end_time(extension.time)
        # extension.timeline.play()
        print("final extension.time: ", extension.time)


    def camera_zoom_out(extension, zoom_ratio: float = 2.0, duration: float = 3, start: float = None):
        """
        Create a camera zoom out animation

        Args:
            zoom_ratio (float): the ratio of the zoom
            duration (float): the duration of the animation in seoconds
            start (float): the start time of the animation in seconds
        """
        print("In camera_zoom_out function")
        # extension.time += 1
        # stage = omni.usd.get_context().get_stage()
        camera = extension.stage.GetPrimAtPath(extension.camera_path)
        focal_length_attr = camera.GetAttribute("focalLength")
        current_focal_length = focal_length_attr.Get()
        new_focal_length = current_focal_length / zoom_ratio
        
        print("initial extension.time: ", extension.time)
        focal_length_attr.Set(value=current_focal_length, time=start if start != None else extension.time)
        extension.timeline.set_start_time(start if start != None else extension.time)
        if start == None: extension.time += duration * extension.stage.GetFramesPerSecond()

        focal_length_attr.Set(value=new_focal_length, time=start+duration if start != None else extension.time)
        extension.timeline.set_end_time(extension.time)
        # extension.timeline.play()
        print("final extension.time: ", extension.time)

    def camera_pan(extension, pan_distance: Gf.Vec2f, duration: float = 3, start: float = None):
        """
        Create a camera pan horizontal or vertical animation
        """
        camera = extension.stage.GetPrimAtPath(extension.camera_path)
        pan_attr = camera.GetAttribute("xformOp:translate")
        current_orientation = pan_attr.Get()
        new_translation = Gf.Vec3f(current_orientation[0] + pan_distance[0], current_orientation[1], current_orientation[2] + pan_distance[1])

        pan_attr.Set(value=current_orientation, time=start if start != None else extension.time)
        if start == None: extension.time += duration * extension.stage.GetFramesPerSecond()
        pan_attr.Set(value=new_translation, time=extension.time)
        extension.time += duration * extension.stage.GetFramesPerSecond()


    def camera_roll(extension, roll_angle: float, duration: float = 3, start: float = None):
        """
        
        """
        camera = extension.stage.GetPrimAtPath(extension.camera_path)
        axis = Gf.Vec3d(0, 0, 1).GetNormalized()
        
        rotation_attr = camera.GetAttribute("xformOp:rotateXYZ")

        current_rotation = rotation_attr.Get()  
        
        print(current_rotation)
        if current_rotation is None:
            new_rotation = Gf.Vec3d(axis[0] * roll_angle, axis[1] * roll_angle, axis[2] * roll_angle)
            rotation_attr.Set(value = Gf.Vec3d(0, 0, 0), time = 0)
        else:
            new_rotation = Gf.Vec3d(current_rotation[0] + axis[0] * roll_angle, current_rotation[1] + axis[1] * roll_angle, current_rotation[1] + axis[2] * roll_angle)
            rotation_attr.Set(value = current_rotation, time = 0)

        extension.time += duration * extension.GetFramesPerSecond()
        rotation_attr.Set(value=new_rotation, time=extension.time)
        extension.time += duration * extension.GetFramesPerSecond()

    def camera_pull_in(extension, pull_distance: float, duration: float = 3, start: float = None):
        """
        Create a camera pull in out animation

        Args:
            pull_distance (float): distance the camera will pull in
            duration (float): the duration of the animation in seoconds
            start (float): the start time of the animation in seconds
        """
        camera_translation_attr = extension.translateOp
        current_translation = camera_translation_attr.Get()
        new_translation = current_translation + Gf.Vec3d(0, 0, -pull_distance)
        
        camera_translation_attr.Set(value=current_translation, time=start if start != None else extension.time)
        extension.timeline.set_start_time(start if start != None else extension.time)
        if start == None: extension.time += duration * extension.stage.GetFramesPerSecond()

        camera_translation_attr.Set(value=new_translation, time=start+duration if start != None else extension.time)
        extension.timeline.set_end_time(extension.time)

    def camera_push_out(extension, push_distance: float, duration: float = 3, start: float = None):
        """
        Create a camera pull away out animation

        Args:
            push_distance (float): distance the camera will pull away
            duration (float): the duration of the animation in seoconds
            start (float): the start time of the animation in seconds
        """
        camera_translation_attr = extension.translateOp
        current_translation = camera_translation_attr.Get(extension.time)
        new_translation = current_translation + Gf.Vec3d(0, 0, push_distance)

        camera_translation_attr.Set(value=current_translation, time=start if start != None else extension.time)
        extension.timeline.set_start_time(start if start != None else extension.time)
        if start == None: extension.time += duration * extension.stage.GetFramesPerSecond()

        camera_translation_attr.Set(value=new_translation, time=start+duration if start != None else extension.time)
        extension.timeline.set_end_time(extension.time)
    
    def camera_push_up(extension, push_distance: float, duration: float = 3, start: float = None):
        """
        Create a camera translate up animation

        Args:
            push_distance (float): distance the camera will translate up
            duration (float): the duration of the animation in seoconds
            start (float): the start time of the animation in seconds
        """
        camera_translation_attr = extension.translateOp
        current_translation = camera_translation_attr.Get(extension.time)
        new_translation = current_translation + Gf.Vec3d(0, push_distance, 0)

        camera_translation_attr.Set(value=current_translation, time=start if start != None else extension.time)
        extension.timeline.set_start_time(start * extension.stage.GetFramesPerSecond() if start != None else extension.time)
        if start == None: extension.time += duration * extension.stage.GetFramesPerSecond()

        camera_translation_attr.Set(value=new_translation, time=start+duration if start != None else extension.time)
        extension.timeline.set_end_time(extension.time)



    #######################################################
    #                   Animation Methods                 #
    #######################################################

    def prim_translate(extension, direction: str, prim_path: str, distance: float, duration: float = 3, start: float = 0):
        """
        Translate a prim up, down, left, right, forward, or backward

        Args:
            direction (str): The direction in which the translate will happen (up, down, left, right, forward, backward)
            prim_path (str): The path of the prim that will be translated
            distance (float): The distance in which the animation will be translated
            duration (float): the duration of the animation in seoconds
            start (float): the start time of the animation in seconds
        """
        def sanitize_for_usd(name: str) -> str:
            # Replace spaces and hyphens with underscores, remove other invalid characters
            sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name.replace('-', '_').replace(' ', '_'))
            # Ensure the name starts with a letter or underscore
            if not sanitized[0].isalpha() and sanitized[0] != '_':
                sanitized = '_' + sanitized
            return sanitized
        prim_path = sanitize_for_usd(prim_path)
        if "/New_Stage" not in prim_path:
            prim_path = "/New_Stage/" + prim_path
        
        print("prim_path: ", prim_path)
        prim = extension.stage.GetPrimAtPath(prim_path)
        prim_attr = UsdGeom.Xformable(prim)

        translate_attr = next(
            (op for op in prim_attr.GetOrderedXformOps() if op.GetOpType() == UsdGeom.XformOp.TypeTranslate),
            None
        )
        if not translate_attr:
            translate_attr = prim_attr.AddTranslateOp()

        initial_translation = Gf.Vec3d(0, 0, 0)
        translate_attr.Set(initial_translation)
        current_translation = translate_attr.Get()

        if direction == "up":
            new_translation = current_translation + Gf.Vec3d(0, distance, 0)
        elif direction == "down":
            new_translation = current_translation + Gf.Vec3d(0, -distance, 0)
        elif direction == "left":
            new_translation = current_translation + Gf.Vec3d(-distance, 0, 0)
        elif direction == "right":
            new_translation = current_translation + Gf.Vec3d(distance, 0, 0)
        elif direction == "forward":
            new_translation = current_translation + Gf.Vec3d(0, 0, distance)
        elif direction == "backward":
            new_translation = current_translation + Gf.Vec3d(0, 0, -distance)
        
        value_to_use = extension.time * extension.stage.GetFramesPerSecond()
        if start != None:
            value_to_use = start * extension.stage.GetFramesPerSecond()
        
        translate_attr.Set(value=current_translation, time=value_to_use)
        extension.timeline.set_start_time(value_to_use)
        print("start: ", start)
        print("duration: ", duration)
        
        value_updated_with_duration = extension.time + duration * extension.stage.GetFramesPerSecond()
        if start != None:
            value_updated_with_duration = (start + duration) * extension.stage.GetFramesPerSecond()

        translate_attr.Set(value=new_translation, time=value_updated_with_duration)
        extension.timeline.set_end_time(value_updated_with_duration)


    def prim_rotate(extension, rotation_axis: str, prim_path: str, roll_angle: float, duration: float = 3, start: float = None):
        """
        Rotate a prim along the X, Y, or Z axis

        Args:
            rotation_axis (str): The axis in which the prim will be rotated (X, Y, or Z)
            prim_path (str): The path of the prim that will be translated
            roll_angle (float): The angle at which the prim will be rotated
            duration (float): the duration of the animation in seoconds
            start (float): the start time of the animation in seconds
        """
        def sanitize_for_usd(name: str) -> str:
            # Replace spaces and hyphens with underscores, remove other invalid characters
            sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name.replace('-', '_').replace(' ', '_'))
            # Ensure the name starts with a letter or underscore
            if not sanitized[0].isalpha() and sanitized[0] != '_':
                sanitized = '_' + sanitized
            return sanitized
        prim_path = sanitize_for_usd(prim_path)
        
        if "/New_Stage" not in prim_path:
            prim_path = "/New_Stage/" + prim_path
        print("prim_path: ", prim_path)
        
        axis = Gf.Vec3d(0, 0, 1).GetNormalized()
        prim = extension.stage.GetPrimAtPath(prim_path)
        prim_attr = UsdGeom.Xformable(prim)
        if rotation_axis == 'Y' or rotation_axis == 'y':
            axis = Gf.Vec3d(0, 1, 0).GetNormalized()
        elif rotation_axis == 'X' or rotation_axis == 'x':
            axis = Gf.Vec3d(1, 0, 0).GetNormalized()
        elif rotation_axis == 'Z' or rotation_axis == 'z':
            axis = Gf.Vec3d(0, 0, 1).GetNormalized()

        rotation_attr = next(
            (op for op in prim_attr.GetOrderedXformOps() if op.GetOpType() == UsdGeom.XformOp.TypeRotateXYZ),
            None
        )
        if not rotation_attr:
            rotation_attr = prim_attr.AddRotateXYZOp()

        initial_rotation = Gf.Vec3d(0.0, 0.0, 0.0)
        rotation_attr.Set(initial_rotation)
        current_rotation = rotation_attr.Get()
        
        print(current_rotation)
        if current_rotation is None:
            new_rotation = Gf.Vec3d(axis[0] * roll_angle, axis[1] * roll_angle, axis[2] * roll_angle)
            rotation_attr.Set(value = initial_rotation, time=start if start != None else extension.time)
        else:
            new_rotation = Gf.Vec3d(current_rotation[0] + axis[0] * roll_angle, current_rotation[1] + axis[1] * roll_angle, current_rotation[1] + axis[2] * roll_angle)
            rotation_attr.Set(value = current_rotation, time=start if start != None else extension.time)

        value_to_use = extension.time * extension.stage.GetFramesPerSecond()
        if start != None:
            value_to_use = start * extension.stage.GetFramesPerSecond()
        
        rotation_attr.Set(value=current_rotation, time=value_to_use)
        extension.timeline.set_start_time(value_to_use)
        print("start: ", start)
        print("duration: ", duration)
        
        value_updated_with_duration = extension.time + duration * extension.stage.GetFramesPerSecond()
        if start != None:
            value_updated_with_duration = (start + duration) * extension.stage.GetFramesPerSecond()

        rotation_attr.Set(value=new_rotation, time=value_updated_with_duration)
        extension.timeline.set_end_time(value_updated_with_duration)

    def keyframe(stage, camera, prim_path: str, attribute_path: str, time: float, value: float) -> None:
        """
        Keyframe an attribute of a prim at a time with a value

        Args:
            prim_path (str): the path of the prim to keyframe
            attribute (str): the attribute to keyframe
            time (float): the time to keyframe
            value (float): the value to keyframe
        """
        stage.DefinePrim(prim_path, "Cube")

        # Get the prim
        prim = stage.GetPrimAtPath(prim_path)
        if not prim.IsValid():
            raise ValueError(f"Prim not found at path: {prim_path}")
        
        if "." in attribute_path:
            prim_attr_path, attr_path_and_component = attribute_path.split(".")
            # print("attr_path_and_component: ", attr_path_and_component)
            if "|" in attr_path_and_component:
                attr_path, attr_component = attr_path_and_component.split("|")  #attr_path: "xformOp:translate"
                # print("attr_path:", attr_path)
                # print("attr_component: ", attr_component)

        print("attr_path:", attr_path)
        # Ensure the prim is a Xformable
        xformable = UsdGeom.Xformable(prim)
        xformable.SetXformOpOrder([])
        # if not "xformOp:translate" in prim.GetAttributes:
        #     xformable = xformable.AddTranslateOp()
        # if not "xformOp:rotateXYZ" in prim.GetAttributes: 
        #     xformable = xformable.AddRotateXYZOp()
        # if not "xformOp:scale" in prim.GetAttributes: 
        #     xformable = xformable.AddScaleOp()

        # Add transform operations if they don't exist
        if attr_path == "xformOp:translate":
            xformable = xformable.AddTranslateOp()
            if attr_component == "x":
                current_value = Gf.Vec3f(value, 0, 0)
            elif attr_component == "y":
                current_value = Gf.Vec3f(0, value, 0)
            else:
                current_value = Gf.Vec3f(0, 0, value)

        elif attr_path == "xformOp:rotateXYZ":
            xformable = xformable.AddRotateXYZOp()
            if attr_component == "x":
                axis = Gf.Vec3d(1, 0, 0).GetNormalized()
                Gf.Quatf(math.cos(value / 2), axis[0] * math.sin(value / 2), axis[1] * math.sin(value / 2), axis[2] * math.sin(value / 2))
            elif attr_component == "y":
                axis = Gf.Vec3d(0, 1, 0).GetNormalized()
                Gf.Quatf(math.cos(value / 2), axis[0] * math.sin(value / 2), axis[1] * math.sin(value / 2), axis[2] * math.sin(value / 2))
            else:
                axis = Gf.Vec3d(0, 0, 1).GetNormalized()
                Gf.Quatf(math.cos(value / 2), axis[0] * math.sin(value / 2), axis[1] * math.sin(value / 2), axis[2] * math.sin(value / 2))
                
        elif attr_path == "xformOp:scale":
            xformable = xformable.AddScaleOp()
            if attr_component == "x":
                current_value = Gf.Vec3f(value, 0, 0)
            elif attr_component == "y":
                current_value = Gf.Vec3f(0, value, 0)
            else:
                current_value = Gf.Vec3f(0, 0, value)
        
        
        print(attr_path_and_component)
        attribute_path = prim_attr_path + "." + attr_path

        # Get the attribute using the full attribute path
        xformable = stage.GetAttributeAtPath(attribute_path)
        if not xformable:
            print(f"Available attributes for {prim_path}:")
            for attr in prim.GetAttributes():
                print(f"  {attr.GetName()}")
            raise ValueError(f"Attribute not found: {attribute_path} on prim {prim_path}")
        
        current_value = Gf.Vec3f(value, value, value)

        # Set the keyframe
        if attr_path == "xformOp:translate" or "xformOp:scale":
            xformable.Set(Gf.Vec3f(0.0, 0.0, 0.0), 0)
            xformable.Set(current_value, Usd.TimeCode(time))
        else:
            xformable.Set(Gf.Quatf(0.0, 0.0, 0.0, 0.0), 0)
            xformable.Set(current_value, Usd.TimeCode(time))

    def create_scale_animation(stage, prim_path: str, duration: float, scale_ratio: float = 2.0) -> None:
        """
        Create a scale animation for a prim

        Args:
            prim_path (str): the path of the prim to animate
            duration (float): the duration of the animation
            scale_ratio (float): the scale ratio
        """
        stage.DefinePrim(prim_path, "Cube")
        prim_object = stage.GetPrimAtPath(prim_path)

        xformable_prim = UsdGeom.Xformable(prim_object)
        xformable_prim.SetXformOpOrder([])
        scale_op = xformable_prim.AddScaleOp(UsdGeom.XformOp.PrecisionFloat)

        start_scale = Gf.Vec3f(0.0, 0.0, 0.0)
        end_scale = Gf.Vec3f(scale_ratio, scale_ratio, scale_ratio)
        
        scale_op.Set(start_scale, 0)
        scale_op.Set(end_scale, duration)



    #######################################################
    #                   Lighting Methods                  #
    #######################################################

    def place_lighting(extension, light_name: str, intensity: float = 1000, 
                       color_red: float = 1, color_green: float = 0, color_blue: float = 0,
                       position_x: float = 0, position_y: float = 200, position_z: float = 500, 
                       rotation_angle_x: float = 0, rotation_angle_y: float = 0, rotation_angle_z: float = 0, exposure: float = 20):
        """
        Create a lighting and place it at a certain position with a specified color and rotation
        
        Args:
            light_name (str): The name of the light
            intensity (float): The intensity at which the light shines
            color_red (float): Red component of the rgb light value for light color
            color_green (float): Green component of the rgb light value for light color
            color_blue (float): Blue component of the rgb light value for light color
            position_x (float): X component of the position of the light
            position_y (float): Y component of the position of the light
            position_z (float): Z component of the position of the light
            rotation_angle_x (float): X component of rotation angle of the light
            rotation_angle_y (float): Y component of rotation angle of the light
            rotation_angle_z (float): Z component of rotation angle of the light
        """
        # Define the light path
        light_path = '/World/' + light_name

        UsdGeom.Xform.Define(extension.stage, light_path)
        light = UsdLux.DiskLight.Define(extension.stage, light_path + "/DiskLight")
        
        light.GetIntensityAttr().Set(intensity)  # Set intensity
        light.AddTranslateOp().Set(Gf.Vec3f([position_x, position_y, position_z]))  # Set position
        light.AddRotateXYZOp().Set(Gf.Vec3f([rotation_angle_x, rotation_angle_y, rotation_angle_z]))
        light.GetColorAttr().Set(Gf.Vec3f([color_red, color_green, color_blue]))  # White light
        light.GetExposureAttr().Set(exposure) # Set exposure

        print(f"Created point light at {[position_x, position_y, position_z]} with intensity {intensity}")
        
        
    #######################################################
    #                 Background Methods                  #
    #######################################################    
    def background(extension, color_red: float = 1, color_green: float = 0.5, color_blue: float = 0.5,
                   light_path: str = "/background", use_hdri: bool = False):
        """
        Create a background and place it around the prim
        
        Args:
            color_red (float): Red component of the rgb light value for light color
            color_green (float): Green component of the rgb light value for light color
            color_blue (float): Blue component of the rgb light value for light color
            light_path (str): The path of the light
            use_hdri (bool): Use hdri background or not
        """
        if use_hdri:
            UsdGeom.Xform.Define(extension.stage, light_path)
            dome_light = UsdLux.DomeLight.Define(extension.stage, light_path + "/DomeLight")
            dome_light.CreateColorAttr(Gf.Vec3f([color_red, color_green, color_blue])) 
            exr_texture_path = "C:/Users/Rithwik Nukala/Downloads/forest.exr"  # Replace with your EXR file path
            dome_light.CreateTextureFileAttr(exr_texture_path)
        else:
            wall1 = UsdGeom.Plane.Define(extension.stage, "/World/wall1")
            wall2 = UsdGeom.Plane.Define(extension.stage, "/World/wall2")
            wall3 = UsdGeom.Plane.Define(extension.stage, "/World/wall3")
            wall4 = UsdGeom.Plane.Define(extension.stage, "/World/wall4")
            roof = UsdGeom.Plane.Define(extension.stage, "/World/roof")
            
            # ground_range = extension.stage.GetPrimAtPath("/Environment/ground").GetExtentAttr().Get().GetRange()
            # print("ground_range: ", ground_range)
            
            wall1_xformable = UsdGeom.Xformable(wall1)
            wall2_xformable = UsdGeom.Xformable(wall2)
            wall3_xformable = UsdGeom.Xformable(wall3)
            wall4_xformable = UsdGeom.Xformable(wall4)
            roof_xformable = UsdGeom.Xformable(roof)
            
            #translate walls
            wall1_translateOp = wall1_xformable.AddTranslateOp()
            wall2_translateOp = wall2_xformable.AddTranslateOp()
            wall3_translateOp = wall3_xformable.AddTranslateOp()
            wall4_translateOp = wall4_xformable.AddTranslateOp()
            roof_translateOp = roof_xformable.AddTranslateOp()
            
            wall1_translateOp.Set(Gf.Vec3d(-700, 700, 0))
            wall2_translateOp.Set(Gf.Vec3d(0, 700, -700))
            wall3_translateOp.Set(Gf.Vec3d(700, 700, 0))
            wall4_translateOp.Set(Gf.Vec3d(0, 700, 700))
            roof_translateOp.Set(Gf.Vec3d(0, 1400, 0))
            
            #scale walls bigger
            wall1_scaleOp = wall1_xformable.AddScaleOp()
            wall2_scaleOp = wall2_xformable.AddScaleOp()
            wall3_scaleOp = wall3_xformable.AddScaleOp()
            wall4_scaleOp = wall4_xformable.AddScaleOp()
            roof_scaleOp = roof_xformable.AddScaleOp()
            
            wall1_scaleOp.Set(Gf.Vec3d(700, 700, 700))
            wall2_scaleOp.Set(Gf.Vec3d(700, 700, 700))
            wall3_scaleOp.Set(Gf.Vec3d(700, 700, 700))
            wall4_scaleOp.Set(Gf.Vec3d(700, 700, 700))
            roof_scaleOp.Set(Gf.Vec3d(700, 700, 700))
            
            #rotate walls
            wall1_rotateOp = wall1_xformable.AddRotateXYZOp()
            wall2_rotateOp = wall2_xformable.AddRotateXYZOp()
            wall3_rotateOp = wall3_xformable.AddRotateXYZOp()
            wall4_rotateOp = wall4_xformable.AddRotateXYZOp()
            roof_rotateOp = roof_xformable.AddRotateXYZOp()
            
            wall1_rotateOp.Set(Gf.Vec3d(0, 90, 0))
            wall2_rotateOp.Set(Gf.Vec3d(0, 0, 0))
            wall3_rotateOp.Set(Gf.Vec3d(0, -90, 0))
            wall4_rotateOp.Set(Gf.Vec3d(0, 180, 0))
            roof_rotateOp.Set(Gf.Vec3d(90, 0, 0))
            
            
            material_path = "/World/WallMaterial"
            material = UsdShade.Material.Define(extension.stage, material_path)
            
            shader = UsdShade.Shader.Define(extension.stage, f"{material_path}/Shader")

            # Define Shader ID and Outputs
            shader.CreateIdAttr("UsdPreviewSurface")
            shader_output = shader.CreateOutput("surface", Sdf.ValueTypeNames.Token)

            # Set Shader Inputs
            shader.CreateInput("emissiveColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(color_red, color_green, color_blue))
            shader.CreateInput("emissiveIntensity", Sdf.ValueTypeNames.Float).Set(200)
            shader.CreateInput("doubleSided", Sdf.ValueTypeNames.Bool).Set(True)
            # skydome.CreateDoubleSidedAttr(defaultValue=True, writeSparsely=False)

            # Bind the Shader to the Material
            material_surface_output = material.CreateSurfaceOutput()
            material_surface_output.ConnectToSource(shader_output)

            # Bind the Material to the Skydome
            UsdShade.MaterialBindingAPI.Apply(wall1.GetPrim()).Bind(material)
            UsdShade.MaterialBindingAPI.Apply(wall2.GetPrim()).Bind(material)
            UsdShade.MaterialBindingAPI.Apply(wall3.GetPrim()).Bind(material)
            UsdShade.MaterialBindingAPI.Apply(wall4.GetPrim()).Bind(material)
            UsdShade.MaterialBindingAPI.Apply(roof.GetPrim()).Bind(material)
            
        
    #######################################################
    #                   Import Asset                      #
    #######################################################      
    def import_asset(extension, prompt) -> str:
        """
        Pull the object from the AWS bucket and load it into the scene
        Args:
            prompt (str): the object the user wants to load
        Return:
            str: the path of the object
        """
        print("prompt inside import asset: ", prompt)
        def add_int_reference(prim: Usd.Prim, ref_target_path: Sdf.Path) -> None:
                references: Usd.References = prim.GetReferences()
                references.AddInternalReference(ref_target_path)

        def add_ext_reference(prim: Usd.Prim, ref_asset_path: str, ref_target_path: Sdf.Path) -> None:
                references: Usd.References = prim.GetReferences()
                references.AddReference(
                    assetPath=ref_asset_path,
                    primPath=ref_target_path # OPTIONAL: Reference a specific target prim. Otherwise, uses the referenced layer's defaultPrim.
                )
        
        def add_reference(stage, local_path, prompt):

            print("in add reference")
            # stage = omni.usd.get_context().get_stage()
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
                
                
        aws_access_id = "AKIA4HMIAHI53YO5JHJG"
        aws_secret_access_id = "gDjGAN+Y9XiOiEpTRJyscym1MDYeT1D/6rWW5uy+"
        region_name = "us-west-1"

        s3 = boto3.client('s3', 
                    aws_access_key_id=aws_access_id,
                    aws_secret_access_key=aws_secret_access_id,
                    region_name=region_name)

        bucket_name = "omni3dvideo"
        prefix = f"Assets/{prompt}"
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

        if 'Contents' not in response:
            print(f"No objects found with prefix '{prefix}'")

        for obj in response['Contents']:
            # Print or return the full S3 URL
            object_key = obj['Key']
            s3_url = f"s3://{bucket_name}/{object_key}"
            break

        s3_object_path = s3_url[len("s3://omni3dvideo/"):]
        print("s3_object_path", s3_object_path)

        pattern = r"(\w+(?:-\w+)?)/([0-9a-f]+)/model\.usd"
        match = re.search(pattern, s3_object_path)
        print("match", match)
        if match:
            prompt = match.group(1)
            hash_value = match.group(2)
            print(f"Prompt: {prompt}")
            print(f"Hash: {hash_value}")
        else:
            print("No match found")

        # New code to dynamically determine texture path
        def get_texture_path_from_s3(bucket_name, base_path):
            texture_prefix = f"{base_path}textures/"
            response = s3.list_objects_v2(Bucket=bucket_name, Prefix=texture_prefix)
            
            for obj in response.get('Contents', []):
                if obj['Key'].endswith(('_texture0.png', '_texture0.jpg')):
                    return obj['Key']
            return None
        
        base_path = f"Assets/{prompt}/{hash_value}/"
        s3_texture_path = get_texture_path_from_s3(bucket_name, base_path)
        print("s3_texture_path", s3_texture_path)

        def sanitize_for_filesystem(name: str) -> str:
            # Replace spaces with hyphens, remove other invalid characters
            return re.sub(r'[^a-zA-Z0-9-]', '-', name.replace(' ', '-')).lower()

        def sanitize_for_usd(name: str) -> str:
            # Replace spaces and hyphens with underscores, remove other invalid characters
            sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name.replace('-', '_').replace(' ', '_'))
            # Ensure the name starts with a letter or underscore
            if not sanitized[0].isalpha() and sanitized[0] != '_':
                sanitized = '_' + sanitized
            return sanitized

        filesystem_prompt = sanitize_for_filesystem(prompt)
        usd_prompt = sanitize_for_usd(prompt)
            
        ext_path = get_extension_path()
        object_asset_folder = f"{ext_path}/downloads/{filesystem_prompt}/models/"
        texture_asset_folder = f"{ext_path}/downloads/{filesystem_prompt}/textures/"    
        os.makedirs(object_asset_folder, exist_ok=True) 
        os.makedirs(texture_asset_folder, exist_ok=True)

        local_object_path = os.path.join(object_asset_folder, f"model.usd").replace("\\", "/")
        if s3_texture_path:
            local_texture_path = os.path.join(texture_asset_folder, os.path.basename(s3_texture_path)).replace("\\", "/")


        if os.path.exists(local_object_path):
            print(f"File already exists at {local_object_path}")
        else:
            print("downloaded")
            s3.download_file(bucket_name, s3_object_path, local_object_path)
        
        if s3_texture_path:
            if os.path.exists(local_texture_path):
                print(f"File already exists at {local_texture_path}")
            else:
                print("second download")
                s3.download_file(bucket_name, s3_texture_path, str(local_texture_path))

        #Start of creating a reference for the prim
        add_reference(extension.stage, local_object_path, usd_prompt)
        if s3_texture_path:
            apply_texture_from_file(f"/New_Stage/{usd_prompt}", local_texture_path)