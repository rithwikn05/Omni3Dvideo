from pathlib import Path
from pxr import Usd, Gf

class transform:
    def rotate(object):
        #rotate along x-axis
        object.AddRotateXOp(oPSuffix = "spin").Set(Gf.Vec3D(0, 1, 0))  #spinning and rotated
        object.AddRotateXop(opSuffix = "tilt").Set(Gf.Vec3D(1, 0, 0))  #tilted spinning

    def scale(object):
        object.AddScaleOp().Set((50, 50, 50))  #Scale everything to be 50 units l, w, h

    def orient(object):
        object.AddOrientOp().Set(0, 1, 0)

layer_path = str(Path.home() / "defining_prims.usda")
stage = Usd.Stage.CreateNew(layer_path)
cube = stage.DefinePrim("/cube", "Cube")
trans = transform()
trans.rotate(cube)
trans.scale(cube)
trans.orient(cube)