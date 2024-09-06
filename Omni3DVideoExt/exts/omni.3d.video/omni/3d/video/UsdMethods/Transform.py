from pathlib import Path
from pxr import Usd, Gf, UsdGeom
import omni.usd
from typing import Optional, List, Tuple


def move_prim(prim_path: str, direction: str, distance: float) -> None:
    """
    Move the prim to a direction by some unit, Y axis is up, X axis is right, Z axis is front
   
    Args:
        prim_path (str): the path of the prim to move
        direction (str): can be up, down, left, right, front, back
        distance (float): a float suggestion the distance to move
    """

    stage = omni.usd.get_context().get_stage()
    prim = stage.GetPrimAtPath(prim_path)
    translate = prim.GetAttribute("xformOp:translate").Get()
    print("[Atomic Functions] translate", translate)
    if direction == "left":
        translate[0] += distance
    elif direction == "right":
        translate[0] -= distance
    elif direction == "front":
        translate[1] += distance
    elif direction == "back":
        translate[1] -= distance
    elif direction == "up":
        translate[2] += distance
    elif direction == "down":
        translate[2] -= 1 * distance
       
    print("[Atomic Functions] translate", translate)
    prim.GetAttribute("xformOp:translate").Set(translate)


def rotate_prim(prim_path: str, axis: str, degree: float) -> None:
    """
    Rotate the prim along an axis by some degree

    Args:
        prim_path (str): the path of the prim to move
        axis (str): can be x, y, z
        degree (float): a float suggestion the Euler degree to rotate
    """

    stage = omni.usd.get_context().get_stage()
    prim = stage.GetPrimAtPath(prim_path)
    rotation_vector = Gf.Vec3f(0.0, 0.0, 0.0)
    if axis == 'x':
        rotation_vector[0] = degree
    elif axis == 'y':
        rotation_vector[1] = degree
    else:
        rotation_vector[2] = degree
    prim.GetAttribute("xformOp:rotate").Set(rotation_vector)
    

def scale_prim(prim_path: str, relative_scale_ratio: float) -> None:
    """
    Scale the prim by a ratio

    Args:
        prim_path (str): the path of the prim to move
        relative_scale_ratio: a float suggestion the scale ratio
    """
    
    stage = omni.usd.get_context().get_stage()
    prim = stage.GetPrimAtPath(prim_path)
    scale_val = prim.GetAttribute("xformOp:scale")
    prim.GetAttribute("xformOp:scale").Set(scale_val*relative_scale_ratio)

def place_prim_on_another(stage, bottom_prim_path: str, top_prim_path: str) -> None:
    """
    Place the prim on another prim

    Args:
        prim_path (str): the path of the prim to move
        another_prim_path (str): the path of the another prim
    
    e.g. place "/apple" on "/table"
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