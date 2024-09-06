from pathlib import Path
from pxr import Usd, UsdGeom, Gf, UsdUtils, Sdf
import omni.usd, omni.timeline
from omni.timeline import get_timeline_interface
import math
import numpy as np


def create_camera_look_at(look_at_prim_path: str, angle: float = 30, distance: float = 50)  -> None:
    """
    Create a camera at a position and make it look at a point

    Args:
        prim_path (str): the path of the object to look at
        angle (float): the angle of the camera 
        distance (float): the distance of the camera
    """
    stage = omni.usd.get_context().get_stage()
    stage.DefinePrim(look_at_prim_path, "Cube")
    cameraPrim = stage.DefinePrim("/camera", "Camera")

    axis = Gf.Vec3d(1, 0, 0).GetNormalized()

    angle_in_radians = math.radians(angle) - math.radians(angle) * 2

    #Getting prims location matrix
    prim = stage.GetPrimAtPath(look_at_prim_path)
    matrix: Gf.Matrix4d = omni.usd.get_world_transform_matrix(prim)
    translate: Gf.Vec3d = matrix.ExtractTranslation()

    camera_xformable = UsdGeom.Xformable(cameraPrim)
    camera_xformable.ClearXformOpOrder()

    #Finding z and y distance translations relative to the prim
    z_dist = distance * math.cos(angle_in_radians)
    y_dist = distance * math.sin(angle_in_radians)
    translation_position = Gf.Vec3f(translate[0], translate[1] - y_dist, translate[2] + z_dist)

    #Finding the quaternion for the camera angle
    camera_angle = Gf.Quatf(math.cos(angle_in_radians / 2), axis[0] * math.sin(angle_in_radians / 2), axis[1] * math.sin(angle_in_radians / 2), axis[2] * math.sin(angle_in_radians / 2))

    #Setting camera translation
    camera_xformable.AddTranslateOp().Set(translation_position)

    #Setting camera angle
    camera_xformable.AddOrientOp().Set(camera_angle)
    return camera_xformable, cameraPrim
