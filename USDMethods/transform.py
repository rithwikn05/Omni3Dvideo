from pathlib import Path
from pxr import Usd, Gf

class transform:
    def rotate(object):
        #rotate along x-axis
        object.AddRotateXOp(oPSuffix = "spin").Set(36.0)  #spinning and rotated
        object.AddRotateYop(opSuffix = "tilt").Set(60.0)  #tilted spinning
        object.AddRotateZop(opSuffix = "roll").Set(60.0)  #rolling spinning

    def scale(object):
        object.AddScaleOp().Set((50, 50, 50))  #Scale everything to be 50 units l, w, h

    def orient(object):
        orientation = Gf.Quatf(1.0, 0.0, 1.0, 0.0)  # Example quaternion
        object.AddOrientOp().Set(orientation)

    def translate(object):
        object.AddTranslateOp().Set(Gf.Vec3f(10.0, 5.0, 15.0))  #translate object by how much specified

layer_path = str(Path.home() / "defining_prims.usda")
stage = Usd.Stage.CreateNew(layer_path)
cube = stage.DefinePrim("/cube", "Cube")
trans = transform()
trans.rotate(cube)
trans.scale(cube)
trans.orient(cube)
trans.translate(cube)