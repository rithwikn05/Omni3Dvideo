from pathlib import Path
from pxr import Usd, Gf
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

def place_prim_on_another(prim_path: str, another_prim_path: str) -> None:
    """
    Place the prim on another prim

    Args:
        prim_path (str): the path of the prim to move
        another_prim_path (str): the path of the another prim
    
    e.g. place "/apple" on "/table"
    """

    ##  hints
    # 1 find the bounding box of prim1 
    # 2 find the bounding box of prim2
    # 3 put prim2 on prim1
    # 
    # Get bounding box from prim
    #    aabb_min, aabb_max = self.__usd_context.compute_path_world_bounding_box(
    #        str(self.__prim_path)
    #    )

    context = omni.usd.get_context()



# class transform:
#     def rotate(self, object, rotation):
#         #rotate along x-axis
#         object.AddRotateXYZOp().Set(Gf.Vec3d(rotation))

#     def scale(self, object, scale):
#         object.AddScaleOp().Set(scale)  #Scale everything to be 50 units l, w, h

#     def orient(self, object):
#         orientation = Gf.Quatf(1.0, 0.0, 1.0, 0.0)  # Example quaternion
#         object.AddOrientOp().Set(orientation)

#     def translate(self, object, translation):
#         object.AddTranslateOp().Set(value=translation)  #translate object by how much specified

# stage = omni.usd.get_context().get_stage()
# cube = stage.DefinePrim("/cube", "Cube")
# trans = transform()
# trans.rotate(cube)
# trans.scale(cube)
# trans.orient(cube)
# trans.translate(cube)