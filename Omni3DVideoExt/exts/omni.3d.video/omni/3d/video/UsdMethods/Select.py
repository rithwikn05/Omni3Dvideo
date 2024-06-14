import omni.usd
import omni.kit
from pxr import UsdGeom
from typing import Optional, List, Tuple

def select_prims(prim_paths: List[str]) -> None:
    """
    Select prims according to prim paths
   
    Args:
        prim_paths (List[str]): prim paths to select.
    """
    selection = omni.usd.get_context().get_selection()
    selection.clear_selected_prim_paths()
    selection.set_selected_prim_paths(prim_paths, True)

def focus_on_selected_prims() -> None:    
    """
    Let the viewport camera focus on selected prims
    """
    from omni.kit.viewport.utility import frame_viewport_selection
    frame_viewport_selection(force_legacy_api=True)
   
   
def hide_selected_prims() -> None:
    """
    Hide selected prims in the viewport
    """
    print("hide selected prims")
    stage = omni.usd.get_context().get_stage()
    selection = omni.usd.get_context().get_selection().get_selected_prim_paths()
    for prim_path in selection:
        prim = stage.GetPrimAtPath(prim_path)
        imageable = UsdGeom.Imageable(prim)
        if imageable:
            if imageable.ComputeVisibility() != UsdGeom.Tokens.invisible:
                imageable.MakeInvisible()

def show_selected_prims() -> None:
    """
    Make selected prims visiable in the viewport
    """
    stage = omni.usd.get_context().get_stage()
    selection = omni.usd.get_context().get_selection().get_selected_prim_paths()
    for prim_path in selection:
        prim = stage.GetPrimAtPath(prim_path)
        imageable = UsdGeom.Imageable(prim)
        if imageable:
            visibility_attribute = prim.GetAttribute("visibility")
            visibility_attribute.Set("inherited")
            imageable.MakeVisible()

def only_show_selected_prims() -> None:
    """
    Only make selected prims visiable in the viewport
    """
    stage = omni.usd.get_context().get_stage()
    for prim in stage.Traverse():
            prim_type = prim.GetTypeName()
            if "light" in prim_type:
                continue
            imageable = UsdGeom.Imageable(prim)
            if imageable:
                if imageable.ComputeVisibility() != UsdGeom.Tokens.invisible:
                    imageable.MakeInvisible()
                   
    show_selected_prims()
   
def show_all_prims() -> None:
    """
    Show all prims in the viewport
    """
    stage = omni.usd.get_context().get_stage()
    for prim in stage.Traverse():
        imageable = UsdGeom.Imageable(prim)
        if imageable:
            imageable.MakeVisible()
   
def translate_select_prims(direction:str, distance:float) -> None:
    """
    Move select prims to a direction by some unit
   
    Args:
        direction (str): can be up, down, left, right, front, back
        distance (float): a float suggestion the distance to move
    """
    stage = omni.usd.get_context().get_stage()
    selection = omni.usd.get_context().get_selection().get_selected_prim_paths()
    for prim_path in selection:
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