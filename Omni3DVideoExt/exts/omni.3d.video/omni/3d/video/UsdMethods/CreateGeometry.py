from pathlib import Path
from pxr import Usd, Sdf
from typing import Optional, List, Tuple
import omni.usd
from pxr import UsdGeom, Gf
from omni.kit.viewport.utility import get_active_viewport, frame_viewport_selection


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








#  select cube1
# 	        selection.set_selected_prim_paths(["/cube1"], True)
# 	        # frame to the selection
# 	        omni.kit.viewport.utility.frame_viewport_selection(viewport_api=viewport_api)

# 	selection = viewport_api.usd_context.get_selection()

# 	viewport_api = viewport_window.viewport_api

# 	viewport_window = omni.kit.viewport.utility.get_active_viewport_window()


# 	omni.kit.commands.execute("DuplicateViewportCameraCommand", viewport_api=viewport_api)



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