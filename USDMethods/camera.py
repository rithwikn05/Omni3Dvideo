from pathlib import Path
from pxr import Usd, UsdGeom

layer_path = str(Path.home() / "defining_prims.usda")
stage = Usd.Stage.CreateNew(layer_path)
cameraPrim = stage.DefinePrim("/camera", "Camera")
camera = UsdGeom.Camera(cameraPrim)

#set focal length
camera.GetFocalLengthAttr().Set(50.0)

#set horizontal aperature
camera.GetHorizontalAperatureAttr().Set(36.0)

#set vertical aperature
camera.GetVerticalAperatureAttr().Set(24.0)

#Set clipping range
camera.GetClippingRangeAttr().Set((0.1, 1000.0))

#save the stage
stage.GetRootLayer().Save()

#To move the camera, you can use the translate, rotate, scale and orient
#attributes of prims to move it around

