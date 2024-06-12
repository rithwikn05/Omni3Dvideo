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

def rotate_prim(prim_path: str, axis: str, degree: float) -> None:
    """
    Rotate the prim along an axis by some degree

    Args:
        prim_path (str): the path of the prim to move
        axis (str): can be x, y, z
        degree (float): a float suggestion the euler degree to rotate
    """

def scale_prim(prim_path: str, relative_scale_ratio: float) -> None:
    """
    Scale the prim by a ratio

    Args:
        prim_path (str): the path of the prim to move
        relative_scale_ratio: a float suggestion the scale ratio
    """

def place_prim_on_another(prim_path: str, another_prim_path: str) -> None:
    """
    Place the prim on another prim

    Args:
        prim_path (str): the path of the prim to move
        another_prim_path (str): the path of the another prim
    
    e.g. place "/apple" on "/table"
    """


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