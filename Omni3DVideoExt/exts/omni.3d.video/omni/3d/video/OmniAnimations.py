from ast import Tuple
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

    def create_camera_rotate_around_object_animation(extension, prim_path: str, duration: float, angle: float = 45, distance: float = 200) -> None:
        """
        Create a camera animation that rotates around an object
        """
        pass
    
    
    def create_camera_look_at(extension, prim_path: str, duration: float = 3, start: float = None)  -> None:
        """
        Create a camera at a position and make it look at a point
        """
        
        def vectors_to_quaternion(x_vec, y_vec, z_vec):
            """
            Convert three orthogonal basis vectors to a quaternion using USD's Gf types.
            
            Args:
                x_vec (Gf.Vec3d): X basis vector
                y_vec (Gf.Vec3d): Y basis vector
                z_vec (Gf.Vec3d): Z basis vector
                
            Returns:
                Gf.Quatd: Quaternion representing the orientation
            """
            # Create rotation matrix
            m00, m01, m02 = x_vec[0], x_vec[1], x_vec[2]
            m10, m11, m12 = y_vec[0], y_vec[1], y_vec[2]
            m20, m21, m22 = z_vec[0], z_vec[1], z_vec[2]
            
            # Calculate quaternion components using the rotation matrix
            tr = m00 + m11 + m22
            
            if tr > 0:
                S = np.sqrt(tr + 1.0) * 2
                w = 0.25 * S
                x = (m21 - m12) / S
                y = (m02 - m20) / S
                z = (m10 - m01) / S
            elif m00 > m11 and m00 > m22:
                S = np.sqrt(1.0 + m00 - m11 - m22) * 2
                w = (m21 - m12) / S
                x = 0.25 * S
                y = (m01 + m10) / S
                z = (m02 + m20) / S
            elif m11 > m22:
                S = np.sqrt(1.0 + m11 - m00 - m22) * 2
                w = (m02 - m20) / S
                x = (m01 + m10) / S
                y = 0.25 * S
                z = (m12 + m21) / S
            else:
                S = np.sqrt(1.0 + m22 - m00 - m11) * 2
                w = (m10 - m01) / S
                x = (m02 + m20) / S
                y = (m12 + m21) / S
                z = 0.25 * S

            return Gf.Quatd(w, x, y, z)
        
        # Get the USD stage
        stage = omni.usd.get_context().get_stage()

        # Retrieve the source and target prims
        source_prim = extension.stage.GetPrimAtPath(extension.camera_path)
        target_prim = extension.stage.GetPrimAtPath(prim_path)

        if not source_prim or not target_prim:
            print('ugh, check create_camera_look_at function, something went wrong')

        # Get the world positions of the source and target prims
        source_xform = UsdGeom.Xformable(source_prim).ComputeLocalToWorldTransform(0)
        target_xform = UsdGeom.Xformable(target_prim).ComputeLocalToWorldTransform(0)

        source_pos = Gf.Vec3d(source_xform.ExtractTranslation())
        target_pos = Gf.Vec3d(target_xform.ExtractTranslation())
        print("target_pos: ", target_pos)

        # Calculate the direction vector from source to target
        direction = target_pos - source_pos
        direction = direction / direction.GetLength()

        # Calculate the rotation needed for the source to look at the target
        up = Gf.Vec3d(0, 0, -1)
        right = Gf.Vec3d(1, 0, 0)
        forward = Gf.Vec3d(0, -1, 0) # Gf.Cross(forward, right)
        rotation_axis = Gf.Cross(forward, direction)
        print("forward: ", forward)
        print("direction: ", direction)
        
        # project source and target into yz-plane
        # x_proj_dir = Gf.Vec3d(0, direction[1], direction[2])
        # x_proj_for = Gf.Vec3d(0, forward[1], forward[2])
        # x_rot = 0
        # if x_proj_dir != Gf.Vec3d(0,0,0):
        #     x_proj_dir = x_proj_dir / x_proj_dir.GetLength()
        #     x_proj_for = x_proj_for / x_proj_for.GetLength()
        #     x_rot = math.degrees(math.acos(x_proj_for[1]) - math.acos(x_proj_dir[1]))
        
        # project source and target into zx-plane2
        y_proj_dir = Gf.Vec3d(direction[0], 0, direction[2])
        y_proj_for = Gf.Vec3d(forward[0], 0, forward[2])
        y_rot = 0
        if y_proj_dir != Gf.Vec3d(0,0,0):
            y_proj_dir = y_proj_dir / y_proj_dir.GetLength()
            y_proj_for = y_proj_for / y_proj_for.GetLength()
            y_rot = math.degrees(math.acos(y_proj_for[2]) - math.acos(y_proj_dir[2]))
        
        # project source and target into xy-plane
        # z_proj_dir = Gf.Vec3d(direction[0], direction[1], 0)
        # z_proj_for = Gf.Vec3d(forward[0], forward[1], 0)
        # z_rot = 0
        # if z_proj_dir != Gf.Vec3d(0,0,0):
        #     z_proj_dir = z_proj_dir / z_proj_dir.GetLength()
        #     z_proj_for = z_proj_for / z_proj_for.GetLength()
        #     z_rot = math.degrees(math.acos(z_proj_for[0]) - math.acos(z_proj_dir[0]))
        
        
        
        original = vectors_to_quaternion(forward, right, up)
        temp = direction - forward
        rtemp = Gf.Vec3d(-temp[2], 0, temp[0])
        rtemp = rtemp / rtemp.GetLength()
        print(temp)
        print(rtemp)
        quatd = vectors_to_quaternion(temp, rtemp, Gf.Cross(temp, rtemp))

        # Handle edge cases
        # if rotation_axis.GetLength() == 0:
        #     rotation_axis = Gf.Vec3d(0, 1, 0)  # Default to Y axis if aligned

        # Add keyframes for position and rotation at the start time
        xform_api = UsdGeom.Xformable(source_prim)
        
        axis = Gf.Cross(forward, direction)
        angle_in_radians = math.acos(Gf.Dot(forward, direction))
        
        # #Finding the quaternion for the camera angle
        camera_angle = Gf.Quatd(math.cos(angle_in_radians / 2), axis[0] * math.sin(angle_in_radians / 2), axis[1] * math.sin(angle_in_radians / 2), axis[2] * math.sin(angle_in_radians / 2))
        xform_api.ClearXformOpOrder()

        
        existing_ops = xform_api.GetOrderedXformOps()

        # Rotation keyframe at start time
        rotation_attr = None
        for op in existing_ops:
            if op.GetOpType() == UsdGeom.XformOp.TypeOrient:
                rotation_attr = op
                break

        # If the translate op doesn't exist, add it
        if rotation_attr is None:
            rotation_attr = xform_api.AddXformOp(UsdGeom.XformOp.TypeOrient, UsdGeom.XformOp.PrecisionDouble)
        
        print("rotation_attr: ", rotation_attr)
        rotation_attr.Set(value=original, time=start)

        # Add keyframes for position and rotation at the end time (look-at position)
        # position_attr.Set(value=target_pos, time=(start+duration))
        rotation_attr.Set(value=camera_angle, time=(start+duration))
        
        # stage = omni.usd.get_context().get_stage()
        # stage.DefinePrim(look_at_prim_path, "Cube")
        # cameraPrim = stage.DefinePrim("/camera", "Camera")

        # axis = Gf.Vec3d(1, 0, 0).GetNormalized()

        # angle_in_radians = math.radians(angle) - math.radians(angle) * 2

        # #Getting prims location matrix
        # prim = stage.GetPrimAtPath(look_at_prim_path)
        # matrix: Gf.Matrix4d = omni.usd.get_world_transform_matrix(prim)
        # translate: Gf.Vec3d = matrix.ExtractTranslation()

        # camera_xformable = UsdGeom.Xformable(cameraPrim)
        # camera_xformable.ClearXformOpOrder()

        # #Finding z and y distance translations relative to the prim
        # z_dist = distance * math.cos(angle_in_radians)
        # y_dist = distance * math.sin(angle_in_radians)
        # translation_position = Gf.Vec3f(translate[0], translate[1] - y_dist, translate[2] + z_dist)

        # #Finding the quaternion for the camera angle
        # camera_angle = Gf.Quatf(math.cos(angle_in_radians / 2), axis[0] * math.sin(angle_in_radians / 2), axis[1] * math.sin(angle_in_radians / 2), axis[2] * math.sin(angle_in_radians / 2))

        # #Setting camera translation
        # camera_xformable.AddTranslateOp().Set(translation_position)

        # #Setting camera angle
        # camera_xformable.AddOrientOp().Set(camera_angle)
        # return camera_xformable, cameraPrim

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
        
        value_to_use = extension.time * extension.stage.GetFramesPerSecond()
        if start != None:
            value_to_use = start * extension.stage.GetFramesPerSecond()
        
        focal_length_attr.Set(value=current_focal_length, time=value_to_use)
        extension.timeline.set_start_time(value_to_use) # TODO: wait, I don't think we want to do this yet.
        value_updated_with_duration = extension.time + duration * extension.stage.GetFramesPerSecond()
        if start != None:
            value_updated_with_duration = (start + duration) * extension.stage.GetFramesPerSecond()
        
        focal_length_attr.Set(value=new_focal_length, time=value_updated_with_duration)
        extension.timeline.set_end_time(value_updated_with_duration)
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
        value_to_use = extension.time * extension.stage.GetFramesPerSecond()
        
        if start != None:
            value_to_use = start * extension.stage.GetFramesPerSecond()
            
        focal_length_attr.Set(value=current_focal_length, time=value_to_use)
        extension.timeline.set_start_time(value_to_use)
        value_updated_with_duration = extension.time + duration * extension.stage.GetFramesPerSecond()
        if start != None:
            value_updated_with_duration = (start + duration) * extension.stage.GetFramesPerSecond()

        focal_length_attr.Set(value=new_focal_length, time=value_updated_with_duration)
        extension.timeline.set_end_time(value_updated_with_duration)
        # extension.timeline.play()
        print("final extension.time: ", value_updated_with_duration)

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
        
        value_to_use = extension.time * extension.stage.GetFramesPerSecond()
        
        if start != None:
            value_to_use = start * extension.stage.GetFramesPerSecond()
        camera_translation_attr.Set(value=current_translation, time=value_to_use)
        
        extension.timeline.set_start_time(value_to_use)
        value_updated_with_duration = extension.time + duration * extension.stage.GetFramesPerSecond()
        if start != None:
            value_updated_with_duration = (start + duration) * extension.stage.GetFramesPerSecond()

        camera_translation_attr.Set(value=new_translation, time=value_updated_with_duration)
        extension.timeline.set_end_time(value_updated_with_duration)

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

        value_to_use = extension.time * extension.stage.GetFramesPerSecond()
        if start != None:
            value_to_use = start * extension.stage.GetFramesPerSecond()
        camera_translation_attr.Set(value=current_translation, time=value_to_use)
        extension.timeline.set_start_time(value_to_use)
        
        value_updated_with_duration = extension.time + duration * extension.stage.GetFramesPerSecond()
        if start != None:
            value_updated_with_duration = (start + duration) * extension.stage.GetFramesPerSecond()

        camera_translation_attr.Set(value=new_translation, time=value_updated_with_duration)
        extension.timeline.set_end_time(value_updated_with_duration)
    
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

        value_to_use = extension.time * extension.stage.GetFramesPerSecond()
        if start != None:
            value_to_use = start * extension.stage.GetFramesPerSecond()
            
        camera_translation_attr.Set(value=current_translation, time=value_to_use)
        extension.timeline.set_start_time(value_to_use)
        
        value_updated_with_duration = extension.time + duration * extension.stage.GetFramesPerSecond()
        if start != None:
            value_updated_with_duration = (start + duration) * extension.stage.GetFramesPerSecond()

        camera_translation_attr.Set(value=new_translation, time=value_updated_with_duration)
        extension.timeline.set_end_time(value_updated_with_duration)



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
                
                
        aws_access_id = 
        aws_secret_access_id = 
        region_name = 

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
            
            
    
    #######################################################
    #                   Place Objects                     #
    #######################################################  
    
    def place_object_on_another_object(stage, bottom_prim_path: str, top_prim_path: str):
        """
        Places one prim on top of another

        Args:
            bottom_prim_path (str): prim on the bottom
            top_prim_path (str): prim on the top
        """
        if not stage.GetPrimAtPath(bottom_prim_path):
            print("In if bottom_prim_path")
            bottom_prim = stage.DefinePrim(bottom_prim_path, "Cube")
        else:
            print("In else bottom_prim_path")
            bottom_prim = stage.GetPrimAtPath(bottom_prim_path)
            print(bottom_prim)

        if not stage.GetPrimAtPath(top_prim_path):
            print("In if top_prim_path")
            top_prim = stage.DefinePrim(top_prim_path, "Sphere")
        else:
            print("In else top_prim_path")
            top_prim = stage.GetPrimAtPath(top_prim_path)

        bottom_imageable = UsdGeom.Imageable(bottom_prim)
        bottom_time = Usd.TimeCode.Default() # The time at which we compute the bounding box
        bottom_bound = bottom_imageable.ComputeWorldBound(bottom_time, UsdGeom.Tokens.default_)
        bottom_bound_range = bottom_bound.ComputeAlignedBox()

        print(bottom_bound_range)

        top_imageable = UsdGeom.Imageable(bottom_prim)
        top_time = Usd.TimeCode.Default() # The time at which we compute the bounding box
        top_bound = top_imageable.ComputeWorldBound(top_time, UsdGeom.Tokens.default_)
        top_bound_range = top_bound.ComputeAlignedBox()

        min_bottom_location_vec = bottom_bound_range.GetMin()
        max_bottom_location_vec = bottom_bound_range.GetMax()

        min_top_location_vec = top_bound_range.GetMin()
        max_top_location_vec = top_bound_range.GetMax()

        displacement_height = (max_top_location_vec[1] - min_top_location_vec[1]) / 2

        translate_location_vec = Gf.Vec3d((max_bottom_location_vec[0] + min_bottom_location_vec[0]) / 2, max_bottom_location_vec[1] + displacement_height, (max_bottom_location_vec[2] + min_bottom_location_vec[2]) / 2)

        xformable_top_prim = UsdGeom.Xformable(top_prim)
        xformable_top_prim.SetXformOpOrder([])
        xformable_top_prim = xformable_top_prim.AddTranslateOp().Set(translate_location_vec)
        
        
        
        
    def focus_on_prim(stage, prim_path: str):
        """
        Focuses on the prim specified

        Args:
            prim_path (str): prim which should be focused on
        """
        # stage = omni.usd.get_context().get_stage()
        # prim = stage.DefinePrim(prim_path, "Cube")
        # camera = stage.DefinePrim("/camera", "Camera")

        # ctx = omni.usd.get_context()
        # # The second arg is unused. Any boolean can be used.
        # ctx.get_selection().set_selected_prim_paths(["/New_Stage/ref_prim"], True)
        # frame_viewport_selection(active_viewport)

        viewport_window = omni.kit.viewport.utility.get_active_viewport_window()
        viewport_api = viewport_window.viewport_api
        selection = viewport_api.usd_context.get_selection()

        selection.set_selected_prim_paths([prim_path], True)
        
        # frame to the selection
        omni.kit.viewport.utility.frame_viewport_selection(viewport_api=viewport_api, padding = 1.5)

        omni.kit.commands.execute("DuplicateViewportCameraCommand", viewport_api=viewport_api)
        
        
    # def create_basic_geometry(geometry_type: str, prim_path: str, translation: Tuple[float], scale: Tuple[float], rotation: Tuple[float]) -> None:
    #     """
    #     Create a cube prim with specified translation, scale and rotation

    #     Args:
    #         geometry_type (str): the type of geometry to create, can be cube, sphere, plane, cylinder
    #         prim_path (str): the path of the prim to create
    #         translation (Tuple[float]): a tuple of 3 floats suggestion the translation of the prim
    #         scale (Tuple[float]): a tuple of 3 floats suggestion the scale of the prim
    #         rotation (Tuple[float]): a tuple of 3 floats suggestion the Euler rotation of the prim
    #     """
    #     stage = omni.usd.get_context().get_stage()
    #     if geometry_type.lower() == "cube":
    #         geometry = UsdGeom.Cube.Define(stage, prim_path)
    #     elif geometry_type.lower() == "sphere":
    #         geometry = UsdGeom.Sphere.Define(stage, prim_path)
    #     elif geometry_type.lower() == "plane":
    #         geometry = UsdGeom.Plane.Define(stage, prim_path)
    #     elif geometry_type.lower() == "cylinder":
    #         geometry = UsdGeom.Cylinder.Define(stage, prim_path)

    #     xform = UsdGeom.Xformable(geometry.GetPrim())
    #     xform.ClearXformOps()
    #     xform.AddTranslateOp().Set((0, 0, 0))
    #     xform.AddOrientOp().Set(Gf.Quatd(1.0))
    #     xform.AddScaleOp().Set((1, 1, 1))

