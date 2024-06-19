from pathlib import Path
from pxr import Usd, UsdGeom, Gf
import omni.usd
import math


def create_camera_look_at(look_at_prim_path: str, angle: float = 45, distance: float = 200) -> None:
    """
    Create a camera at a position and make it look at a point

    Args:
        prim_path (str): the path of the object to look at
        angle (float): the angle of the camera 
        distance (float): the distance of the camera
    """
    stage = omni.usd.get_context().get_stage()
    look_at_prim = stage.GetPrimAtPath(look_at_prim_path)

    x_dist = distance * math.cos(angle)
    y_dist = distance * math.sin(angle)
    camera_position = Gf.Vec3d(x_dist, y_dist, 0.0)

    target_position = Gf.Vec3d(0.0, 0.0, 0.0)
    direction = target_position - camera_position
    direction.Normalize()

    transform = Gf.Matrix4d(1.0)
    #Rotating camera to the specified angle
    # transform.SetRotate(Gf.Rotation(Gf.Vec3f(0, 0, -1)), direction)
    #Moving camera to the required distance
    transform.SetTranslate(camera_position)

    xformable_obj = UsdGeom.Xformable(look_at_prim_path)
    xformable_obj.SetXformOpOrder([])  #Reset any past transformations done
    xformable_obj.AddTransformOp().Set(transform)


def create_camera_rotate_around_object_animation(prim_path: str, duration: float, angle: float = 45, distance: float = 200) -> None:
    """
    Create a camera animation that rotates around an object
    """


class camera:
    def __init__(self):
        self.stage = omni.usd.get_context().get_stage()

    def getCameraPrim(self):
        cameraPrim = self.stage.DefinePrim("/camera", "Camera")
        camera = UsdGeom.Camera(cameraPrim)
        return camera
    
    def setFocalLength(self, camera, focalLength):
        camera.GetFocalLengthAttr().Set(focalLength)

    #set horizontal aperature
    def setHorizAperature(self, camera, horizAperature):
        camera.GetHorizontalApertureAttr().Set(horizAperature)

    #set vertical aperature
    def setVertAperature(self, camera, vertAperature):
        camera.GetVerticalApertureAttr().Set(vertAperature)

    #Set clipping range
    def setClippingRange(self, camera, range):
        camera.GetClippingRangeAttr().Set(range)

    #save the stage
    def saveStage(self):
        self.stage.GetRootLayer().Save()

#To move the camera, you can use the translate, rotate, scale and orient
#attributes of prims to move it around