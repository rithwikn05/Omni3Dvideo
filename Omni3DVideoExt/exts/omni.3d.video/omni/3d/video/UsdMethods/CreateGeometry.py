from pathlib import Path
from pxr import Usd, Sdf
from typing import Optional, List, Tuple
import omni.usd
from pxr import UsdGeom, Gf


def create_basic_geometry(geometry_type: str, prim_path: str, translation: Tuple[float], scale: Tuple[float], rotation: Tuple[float]) -> None:
    """
    Create a cube prim with specified translation, scale and rotation

    Args:
        geometry_type (str): the type of geometry to create, can be cube, sphere, plane, cylinder
        prim_path (str): the path of the prim to create
        translation (Tuple[float]): a tuple of 3 floats suggestion the translation of the prim
        scale (Tuple[float]): a tuple of 3 floats suggestion the scale of the prim
        rotation (Tuple[float]): a tuple of 3 floats suggestion the Euler rotation of the prim
    """
    stage = omni.usd.get_context().get_stage()
    if geometry_type.lower() == "cube":
        geometry = UsdGeom.Cube.Define(stage, prim_path)
    elif geometry_type.lower() == "sphere":
        geometry = UsdGeom.Sphere.Define(stage, prim_path)
    elif geometry_type.lower() == "plane":
        geometry = UsdGeom.Plane.Define(stage, prim_path)
    elif geometry_type.lower() == "cylinder":
        geometry = UsdGeom.Cylinder.Define(stage, prim_path)

    xform = UsdGeom.Xformable(geometry.GetPrim())
    xform.ClearXformOps()
    xform.AddTranslateOp().Set((0, 0, 0))
    xform.AddOrientOp().Set(Gf.Quatd(1.0))
    xform.AddScaleOp().Set((1, 1, 1))
    

# class createAssets:
#     def __init__(self):
#         self.stage = omni.usd.get_context().get_stage()
#     #Creating basic geometry
#     def create_cube(self, name:str):
#         """
#         Creates a cube object and places it on the stage

#         Args:
#             name (str): Name of the cube prim
#         """
#         cube: Usd.Prim = self.stage.DefinePrim(name, "Cube")
#         self.stage.Save()
#         return cube

#     def create_plane(self, name:str):
#         """
#         Creates a place object and places it on the stage

#         Args:
#             name (str): Name of the cube prim
#         """
#         self.stage.DefinePrim(name, "Plane")
#         self.stage.Save()

#     def create_sphere(self, name:str):
#         """
#         Creates a sphere object and places it on the stage

#         Args:
#             name (str): Name of the cube prim
#         """
#         sphere: Usd.Prim = self.stage.DefinePrim(name, "Sphere")
#         self.stage.Save()
#         return sphere

#     def get_cube_from_prim_path(self, name:str):
#         """
#         Creates a cube object and places it on the stage

#         Args:
#             name (str): Name of the cube prim
#         """
#         cube: Usd.Prim = self.stage.DefinePrim(name, "Cube")   #Here we are using a cube object
#         cube_path = cube.GetPath()   #Gets the path of the cube that we created above
#         box: Usd.Prim = self.stage.GetPrimAthPath(cube_path)  #Get the prim at the specified path
#         print(box)  #prints the prim object at the path that is specified

#     #Importing assets
#     def add_reference(self, name:str):
#         """
#         Imports assets from the specified location to the stage

#         Args:
#             name (str): Name of the cube prim
#         """
#         cube = self.stage.DefinePrim("/cube", "Cube")
#         ref = Sdf.Reference(name, "/ReferencedPrim")  # Here ReferencedPrim would be the cube path
#         cube.GetReference().AddReference(ref)

#     def add_payload(self, name:str):
#         """
#         Adds the specified payload to to the stage. 

#         Args:
#             name (str): Name of the cube prim
#         """
#         cube = self.stage.DefinePrim("/cube", "Cube")
#         payload = Sdf.Payload(name, "/ReferencedPrim")   # Here ReferencedPrim would be the cube path
#         cube.GetPayload().AddPayload(payload)
#         self.stage.Load("/cube")  #loading payload

#     def unload(self, name:str):
#         """
#         Unloads a prim from the scene

#         Args:
#             name (str): Name of the cube prim
#         """
#         self.stage.Unload("/cube")  #Unloading payload