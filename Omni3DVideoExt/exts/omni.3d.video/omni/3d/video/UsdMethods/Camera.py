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
    look_at_prim = stage.DefinePrim(look_at_prim_path, "Cube")
    cameraPrim = stage.DefinePrim("/camera", "Camera")

    x_dist = distance * math.cos(angle)
    y_dist = distance * math.sin(angle)
    camera_position = Gf.Vec3f(x_dist, y_dist, 0.0)

    camera_xform = UsdGeom.Xform(cameraPrim)
    camera_xform.ClearXformOpOrder()

    target_position = Gf.Vec3f(0.0, 0.0, 0.0)
    direction = target_position - camera_position
    print(type(direction))
    # direction = direction.Normalize()

    z_axis = -direction
    up_vector = Gf.Vec3f(0, 0, 1)
    x_axis = Gf.GetNormalized(Gf.Cross(up_vector, z_axis))
    print(type(x_axis))
    y_axis = Gf.Cross(z_axis, x_axis)

    rotation_matrix = Gf.Matrix3f(
        x_axis[0], x_axis[1], x_axis[2],
        y_axis[0], y_axis[1], y_axis[2],
        z_axis[0], z_axis[1], z_axis[2]
    )
    rotation_quat = Gf.Quatf(rotation_matrix)  #Error: Quatf cannot take in Matrix3f

    camera_xform.AddOrientOp().Set(rotation_quat)
    camera_xform.AddTranslateOp().Set(camera_position)


def create_camera_rotate_around_object_animation(prim_path: str, duration: float, angle: float = 45, distance: float = 200) -> None:
    """
    Create a camera animation that rotates around an object
    """

    #First make the camera look at the prim
    create_camera_look_at(prim_path, angle, distance)
    stage = omni.usd.get_context().get_stage()
    cameraPrim = stage.DefinePrim("/camera", "Camera")



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