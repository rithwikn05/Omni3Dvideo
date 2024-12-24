from pxr import UsdGeom, Usd, Gf
import omni.usd, omni.timeline
from omni.timeline import get_timeline_interface
import math
import numpy as np

def create_camera_rotate_around_object_animation(camera_path: str, prim_path: str, duration: float, angle: float = 45, distance: float = 200) -> None:
    """
    Create a camera animation that rotates around an object
    """
    stage = omni.usd.get_context().get_stage()
    cameraPrim = stage.DefinePrim(camera_path, "Camera")
    prim = stage.DefinePrim(prim_path, "Cube")

    timeline = get_timeline_interface()

    camera_xformable = UsdGeom.Xformable(cameraPrim)
    camera_xformable.SetXformOpOrder([])

    translate_op = camera_xformable.AddTranslateOp()
    orient_op = camera_xformable.AddOrientOp()

    # angle_in_radians = math.radians(angle) - math.radians(angle) * 2

    # matrix: Gf.Matrix4d = omni.usd.get_world_transform_matrix(prim)
    target_prim_xform_mat = UsdGeom.Xformable(prim).GetLocalTransformation()
    translate = target_prim_xform_mat.ExtractTranslation()
    print(translate)

    # z_dist = distance * math.cos(angle_in_radians)
    # y_dist = distance * math.sin(angle_in_radians)
    # translation_position = Gf.Vec3f(translate[0], translate[1] - y_dist, translate[2] + z_dist)

    frames_per_second = timeline.get_time_codes_per_seconds()
    start_time = timeline.get_start_time()
    end = start_time + (duration * frames_per_second)

    # new_translation = translation_position
    up_direction = Gf.Vec3d(0, 1, 0)
    timeline.pause()

    for current_time in np.arange(start_time, end, 1/frames_per_second):#int(start_time * frames_per_second), int(end * frames_per_second)):
        rotation_angle_radians = math.radians(angle * ((current_time - start_time) / duration))

        new_z_dist = distance * math.cos(rotation_angle_radians)      
        new_y_dist = distance * math.sin(rotation_angle_radians)

        new_translation = Gf.Vec3d(translate[0], translate[1] + new_y_dist, translate[2] + new_z_dist)
        print(new_translation)
        # print(up_direction)
        # new_rotation = Gf.Quatf(math.cos(rotation_angle_radians / 2), axis[0] * math.sin(rotation_angle_radians / 2), axis[1] * math.sin(rotation_angle_radians / 2), axis[2] * math.sin(rotation_angle_radians / 2))
        
        look_at = Gf.Matrix4d(1.0)
        print(look_at)
        look_at = look_at.SetLookAt(new_translation, translate, up_direction)       
        new_rotation = look_at.ExtractRotation().GetQuat()
        new_rotation = Gf.Quatf(new_rotation)

        timeline.set_current_time(current_time)

        translate_op.Set(new_translation)
        orient_op.Set(new_rotation)
        
    timeline.set_auto_update(True)
    timeline.set_start_time(start_time)
    timeline.set_end_time(end)

def camera_zoom_in(camera_path: str, zoom_ratio: float = 2.0, duration: float = 3):
    """
    Create a camera zoom in animation

    Args:
        camera_path (str): the path of the camera
        zoom_ratio (float): the ratio of the zoom
        duration (float): the duration of the animation in seoconds
    """
    camera_path = "/perspectivecamera"

    stage = omni.usd.get_context().get_stage()
    camera = stage.GetPrimAtPath(camera_path)
    if not (camera and camera.IsValid()):
        camera = stage.DefinePrim(camera_path, "Camera")
        camera_xformable = UsdGeom.Xformable(camera)
        camera_xformable.AddTranslateOp().Set(time = 0, value = Gf.Vec3d(0, 0, 50))

    focal_length_attr = camera.GetAttribute("focalLength")
    current_focal_length = focal_length_attr.Get()
    new_focal_length = current_focal_length * zoom_ratio

    focal_length_attr.Set(value=current_focal_length, time=curr_time)
    curr_time += duration * stage.GetFramesPerSecond()
    focal_length_attr.Set(value=new_focal_length, time=curr_time)


def camera_zoom_out(camera_path: str, zoom_ratio: float = 2.0, duration: float = 3):
    """
    Create a camera zoom out animation
    # Args:
    #     camera_path (str): the path of the camera
    #     zoom_ratio (float): the ratio of the zoom
    #     duration (float): the duration of the animation in seoconds
    """
    camera_path = "/perspectivecamera"
    stage = omni.usd.get_context().get_stage()
    camera = stage.GetPrimAtPath(camera_path)
    if not (camera and camera.IsValid()):
        camera = stage.DefinePrim(camera_path, "Camera")
        camera_xformable = UsdGeom.Xformable(camera)
        camera_xformable.AddTranslateOp().Set(time = 0, value = Gf.Vec3d(0, 0, 50))

    focal_length_attr = camera.GetAttribute("focalLength")
    current_focal_length = focal_length_attr.Get()
    new_focal_length = current_focal_length / zoom_ratio

    focal_length_attr.Set(value=current_focal_length, time=0)

    end_time = duration * stage.GetFramesPerSecond()
    focal_length_attr.Set(value=new_focal_length, time=end_time)

def camera_pan(camera_path: str, pan_distance: Gf.Vec2f, duration: float = 3):
    """
    Create a camera pan horizontal or vertical animation
    """
    stage = omni.usd.get_context().get_stage()
    camera = stage.DefinePrim(camera_path, "Camera")
    camera_xformable = UsdGeom.Xformable(camera)
    camera_xformable.AddTranslateOp().Set(Gf.Vec3d(0, 0, 50))

    pan_attr = camera.GetAttribute("xformOp:translate")
    current_orientation = pan_attr.Get()
    new_translation = Gf.Vec3f(current_orientation[0] + pan_distance[0], current_orientation[1], current_orientation[2] + pan_distance[1])

    pan_attr.Set(value=current_orientation, time=0)

    end_time = duration * stage.GetFramesPerSecond()
    pan_attr.Set(value=new_translation, time=end_time)


def camera_roll(camera_path: str, roll_angle: float, duration: float = 3):
    """
    
    """
    stage = omni.usd.get_context().get_stage()
    camera = stage.DefinePrim(camera_path, "Camera")
    axis = Gf.Vec3d(0, 0, 1).GetNormalized()
    camera_xformable = UsdGeom.Xformable(camera)
    camera_xformable.AddRotateXYZOp().Set(Gf.Vec3d(0, 0, 50))
    
    rotation_attr = camera.GetAttribute("xformOp:rotateXYZ")

    current_rotation = rotation_attr.Get()  
    
    print(current_rotation)
    if current_rotation is None:
        new_rotation = Gf.Vec3d(axis[0] * roll_angle, axis[1] * roll_angle, axis[2] * roll_angle)
        rotation_attr.Set(value = Gf.Vec3d(0, 0, 0), time = 0)
    else:
        new_rotation = Gf.Vec3d(current_rotation[0] + axis[0] * roll_angle, current_rotation[1] + axis[1] * roll_angle, current_rotation[1] + axis[2] * roll_angle)
        rotation_attr.Set(value = current_rotation, time = 0)

    end_time = duration * stage.GetFramesPerSecond()
    rotation_attr.Set(value = new_rotation, time = end_time)

def camera_pull_in(camera_path: str, pull_distance: float, duration: float = 3):
    """
    
    """
    stage = omni.usd.get_context().get_stage()
    camera = stage.DefinePrim(camera_path, "Camera")
    camera_xformable = UsdGeom.Xformable(camera)
    camera_xformable.AddTranslateOp().Set(Gf.Vec3d(50, 50, 5000))

    translation_attr = camera.GetAttribute("xformOp:translate")
    current_translation = translation_attr.Get()
    new_translation = current_translation + Gf.Vec3d(0, 0, pull_distance)

    translation_attr.Set(value=current_translation, time=0)

    end_time = duration * stage.GetFramesPerSecond()
    translation_attr.Set(value=new_translation, time=end_time)

def camera_push_out(camera_path: str, push_distance: float, duration: float = 3):
    """
    
    """
    stage = omni.usd.get_context().get_stage()
    camera = stage.DefinePrim(camera_path, "Camera")
    camera_xformable = UsdGeom.Xformable(camera)
    camera_xformable.AddTranslateOp().Set(Gf.Vec3d(50, 50, 5000))

    translation_attr = camera.GetAttribute("xformOp:translate")
    current_translation = translation_attr.Get()
    new_translation = current_translation + Gf.Vec3d(0, 0, push_distance)

    translation_attr.Set(value=current_translation, time=0)

    end_time = duration * stage.GetFramesPerSecond()
    translation_attr.Set(value=new_translation, time=end_time)