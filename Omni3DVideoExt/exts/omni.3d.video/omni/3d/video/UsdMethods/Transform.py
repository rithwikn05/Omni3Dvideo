from pathlib import Path
from pxr import Usd, Gf
import omni.usd

class transform:
    def rotate(self, object, rotation):
        #rotate along x-axis
        object.AddRotateXYZOp().Set(Gf.Vec3d(rotation))

    def scale(self, object, scale):
        object.AddScaleOp().Set(scale)  #Scale everything to be 50 units l, w, h

    def orient(self, object):
        orientation = Gf.Quatf(1.0, 0.0, 1.0, 0.0)  # Example quaternion
        object.AddOrientOp().Set(orientation)

    def translate(self, object, translation):
        object.AddTranslateOp().Set(value=translation)  #translate object by how much specified

# stage = omni.usd.get_context().get_stage()
# cube = stage.DefinePrim("/cube", "Cube")
# trans = transform()
# trans.rotate(cube)
# trans.scale(cube)
# trans.orient(cube)
# trans.translate(cube)