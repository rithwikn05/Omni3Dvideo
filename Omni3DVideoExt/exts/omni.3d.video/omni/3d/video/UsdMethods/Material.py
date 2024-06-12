from pathlib import Path
from pxr import Usd, Sdf

layer_path = str(Path.home() / "defining_prims.usda")
stage = Usd.Stage.CreateNew(layer_path)

#Not really too sure about this one
class materialAndTexture:
    def createMaterialAndTexture(material):
        material = UsdShade.Material.Define(stage, material)  #define material
        pbrShader = UsdShade.Shader.Define(stage, '/TexModel/boardMat/PBRShader')
        pbrShader.CreateIdAttr("UsdPreviewSurface")
        pbrShader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.4)
        pbrShader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)

        material.CreateSurfaceOutput().ConnectToSource(pbrShader.ConnectableAPI(), "surface")