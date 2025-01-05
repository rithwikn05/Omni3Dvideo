from pxr import UsdGeom, Usd, Gf, Sdf
import omni.usd, omni.timeline
from omni.timeline import get_timeline_interface
import math
import numpy as np


class Omni3DVideo():
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
            camera_path (str): the path of the camera
            zoom_ratio (float): the ratio of the zoom
            duration (float): the duration of the animation in seoconds
        """
        print("In camera_zoom_in function")
        # stage = omni.usd.get_context().get_stage()
        camera = extension.stage.GetPrimAtPath(extension.camera_path)
        focal_length_attr = camera.GetAttribute("focalLength")
        current_focal_length = focal_length_attr.Get()
        new_focal_length = current_focal_length * zoom_ratio

        print("initial extension.time: ", extension.time)
        focal_length_attr.Set(value=current_focal_length, time=start if start else extension.time)
        extension.timeline.set_start_time(start if start else extension.time) # TODO: wait, I don't think we want to do this yet.
        if not start: extension.time += duration
        
        focal_length_attr.Set(value=new_focal_length, time=start+duration if start else extension.time)
        extension.timeline.set_end_time(extension.time)
        extension.timeline.play()
        print("final extension.time: ", extension.time)


    def camera_zoom_out(extension, zoom_ratio: float = 2.0, duration: float = 3, start: float = None):
        """
        Create a camera zoom out animation
        # Args:
        #     camera_path (str): the path of the camera
        #     zoom_ratio (float): the ratio of the zoom
        #     duration (float): the duration of the animation in seoconds
        """
        print("In camera_zoom_out function")
        # extension.time += 1
        # stage = omni.usd.get_context().get_stage()
        camera = extension.stage.GetPrimAtPath(extension.camera_path)
        focal_length_attr = camera.GetAttribute("focalLength")
        current_focal_length = focal_length_attr.Get()
        new_focal_length = current_focal_length / zoom_ratio
        
        print("initial extension.time: ", extension.time)
        focal_length_attr.Set(value=current_focal_length, time=extension.time)
        extension.timeline.set_start_time(extension.time)
        extension.time += duration

        focal_length_attr.Set(value=new_focal_length, time=extension.time)
        extension.timeline.set_end_time(extension.time)
        extension.timeline.play()
        print("final extension.time: ", extension.time)

    def camera_pan(extension, pan_distance: Gf.Vec2f, duration: float = 3, start: float = None):
        """
        Create a camera pan horizontal or vertical animation
        """
        camera = extension.stage.GetPrimAtPath(extension.camera_path)
        pan_attr = camera.GetAttribute("xformOp:translate")
        current_orientation = pan_attr.Get()
        new_translation = Gf.Vec3f(current_orientation[0] + pan_distance[0], current_orientation[1], current_orientation[2] + pan_distance[1])

        pan_attr.Set(value=current_orientation, time=extension.time)
        extension.time += duration# * extension.stage.GetFramesPerSecond()
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
        Move towards a prim using a translation
        """
        camera_translation_attr = extension.translateOp
        current_translation = camera_translation_attr.Get()
        new_translation = current_translation + Gf.Vec3d(0, 0, -pull_distance)
        
        camera_translation_attr.Set(value=current_translation, time=extension.time)
        extension.timeline.set_start_time(extension.time)
        extension.time += duration * extension.stage.GetFramesPerSecond()

        camera_translation_attr.Set(value=new_translation, time=extension.time)
        extension.timeline.set_end_time(extension.time)

    def camera_push_out(extension, push_distance: float, duration: float = 3, start: float = None):
        """
        Move away from a prim using a translation
        """
        camera_translation_attr = extension.translateOp
        current_translation = camera_translation_attr.Get(extension.time)
        new_translation = current_translation + Gf.Vec3d(0, 0, push_distance)

        camera_translation_attr.Set(value=current_translation, time=extension.time)
        extension.timeline.set_start_time(extension.time)
        extension.time += duration * extension.stage.GetFramesPerSecond()

        camera_translation_attr.Set(value=new_translation, time=extension.time)
        extension.timeline.set_end_time(extension.time)
    
    def camera_push_up(extension, push_distance: float, duration: float = 3, start: float = None):
        """
        Move away from a prim using a translation
        """
        camera_translation_attr = extension.translateOp
        current_translation = camera_translation_attr.Get(extension.time)
        new_translation = current_translation + Gf.Vec3d(0, push_distance, 0)

        camera_translation_attr.Set(value=current_translation, time=extension.time)
        extension.timeline.set_start_time(extension.time)
        extension.time += duration * extension.stage.GetFramesPerSecond()

        camera_translation_attr.Set(value=new_translation, time=extension.time)
        extension.timeline.set_end_time(extension.time)



    #######################################################
    #                   Animation Methods                 #
    #######################################################

    def prim_translate(extension, direction: str, prim_path: str, distance: float, duration: float = 3, start: float = None):
        """
        Translate a prim up, down, left, right, forward, or backward
        """
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
        
        translate_attr.Set(value=current_translation, time=extension.time)
        extension.timeline.set_start_time(extension.time)
        extension.time += duration * extension.stage.GetFramesPerSecond()

        translate_attr.Set(value=new_translation, time=extension.time)
        extension.timeline.set_end_time(extension.time)

    def prim_roll(extension, rotation_axis: str, prim_path: str, roll_angle: float, duration: float = 3, start: float = None):
        """
        
        """
        prim = extension.stage.GetPrimAtPath(prim_path)
        prim_attr = UsdGeom.Xformable(prim)
        if rotation_axis == 'Y':
            axis = Gf.Vec3d(0, 1, 0).GetNormalized()
        elif rotation_axis == 'X':
            axis = Gf.Vec3d(1, 0, 0).GetNormalized()
        elif rotation_axis == 'Z':
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
            rotation_attr.Set(value = initial_rotation, time = extension.time)
        else:
            new_rotation = Gf.Vec3d(current_rotation[0] + axis[0] * roll_angle, current_rotation[1] + axis[1] * roll_angle, current_rotation[1] + axis[2] * roll_angle)
            rotation_attr.Set(value = current_rotation, time = extension.time)

        extension.timeline.set_start_time(extension.time)
        extension.time += duration * extension.stage.GetFramesPerSecond()

        rotation_attr.Set(value=new_rotation, time=extension.time)
        extension.timeline.set_end_time(extension.time)

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

        # xformable.SetXformOpOrder([])
        
    def create_movement_animation(stage, prim_path: str, duration: float, direction: str = "X", distance: float = 2000.0) -> None:
        """
        Create a movement animation for a prim

        Args:
            prim_path (str): the path of the prim to animate
            duration (float): the duration of the animation
            direction (str): the direction to move
            distance (float): the distance to move
        """
        stage.DefinePrim(prim_path, "Cube")
        prim_object = stage.GetPrimAtPath(prim_path)

        xformable_object = UsdGeom.Xformable(prim_object)
        xformable_object.SetXformOpOrder([])
        xformable_object = xformable_object.AddTranslateOp()

        # Create or get the translate operation
        translate_attr = prim_object.GetAttribute("xformOp:translate").Get()

        start_position = Gf.Vec3f(0.0, 0.0, 0.0)
        end_position = Gf.Vec3f(start_position)
        if direction == "X":
            end_position[0] += distance
        elif direction == "Y":
            end_position[1] += distance
        elif direction == "Z":
            end_position[2] += distance

        xformable_object.Set(start_position, 0)
        xformable_object.Set(end_position, duration)

        
    def create_rotation_animation(stage, prim_path: str, duration: float, axis: str = "Y", degree: float = 180) -> None:
        """
        Create a 360 degree rotation animation for a prim

        Args:
            prim_path (str): the path of the prim to animate
            duration (float): the duration of the animation
            axis (str): the axis to rotate
        """
        stage.DefinePrim(prim_path, "Cube")
        prim_object = stage.GetPrimAtPath(prim_path)

        angle_in_radians = math.radians(degree) - math.radians(degree) * 2

        xformable_prim = UsdGeom.Xformable(prim_object)
        xformable_prim.SetXformOpOrder([])

        if axis.lower() == "x":
            axis = Gf.Vec3d(1, 0, 0).GetNormalized()
        elif axis.lower() == "y":
            axis = Gf.Vec3d(0, 1, 0).GetNormalized()
        elif axis.lower() == "z":
            axis = Gf.Vec3d(0, 0, 1).GetNormalized()
        
        new_angle = Gf.Quatf(math.cos(angle_in_radians / 2), axis[0] * math.sin(angle_in_radians / 2), axis[1] * math.sin(angle_in_radians / 2), axis[2] * math.sin(angle_in_radians / 2))
        xformable_prim = xformable_prim.AddOrientOp()
        
        xformable_prim.Set(Gf.Quatf(0.0, 0.0, 0.0, 0.0), 0)
        xformable_prim.Set(new_angle, duration)

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