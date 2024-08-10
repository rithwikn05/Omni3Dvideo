from pathlib import Path
from pxr import Usd, Sdf, UsdShade
import uuid
import logging

import omni.usd

from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)

def add_material(prim_path: str, diffuse_color: Tuple[float]) -> None:
    """
    Add a material to a prim with basic color
    
    Args:
        prim_path (str): the path of the prim to create
        diffuse_color (Tuple[float]): a tuple of RGB floats suggestion the color of the material
    """
    stage = omni.usd.get_context().get_stage()

     # bind material and texture
    stage = omni.usd.get_context().get_stage()
    mtl_random_name = str(uuid.uuid4())[:3]
    mtl_path = Sdf.Path(f"/World/Looks/GenAI_OmniPBR_{mtl_random_name}")
    mtl = UsdShade.Material.Define(stage, mtl_path)
    shader = UsdShade.Shader.Define(stage, mtl_path.AppendPath("Shader"))
    # shader.CreateImplementationSourceAttr(UsdShade.Tokens.sourceAsset)
    shader.SetSourceAsset("OmniPBR.mdl", "mdl")
    shader.SetSourceAssetSubIdentifier("OmniPBR", "mdl")
    shader.CreateInput("diffuse_color_constant", Sdf.ValueTypeNames.Color3f).Set(diffuse_color)

    mtl.CreateSurfaceOutput("mdl").ConnectToSource(shader.ConnectableAPI(), "out")
    mtl.CreateDisplacementOutput("mdl").ConnectToSource(shader.ConnectableAPI(), "out")
    mtl.CreateVolumeOutput("mdl").ConnectToSource(shader.ConnectableAPI(), "out")

    # bind the material to the prim
    UsdShade.MaterialBindingAPI(stage.GetPrimAtPath(prim_path)).Bind(mtl, UsdShade.Tokens.strongerThanDescendants)





def generate_texture(prim_path: str, text: str = "A chubby orange cat riding through space, digital art") -> None:
    """
    Generate a texture for a prim
    
    Args:
        prim_path (str): the path of the prim to create
        text (str): the description of the texture
    """

    from ..GenAI.image_generator import ImageGenerator
    image_generator = ImageGenerator()

    from ..env import NGC_API_KEY
    invoke_url = "https://ai.api.nvidia.com/v1/genai/stabilityai/stable-diffusion-xl"
    image_generator.set_invoke_url(invoke_url)
    image_generator.set_api_key(NGC_API_KEY)
    image_generator.set_headers()
    image_generator.set_payload(prompt=text)

    from ..utils import get_extension_path
    output_image_folder = get_extension_path() / "output"

    # check if the output folder exists, if not, create it
    if not output_image_folder.exists():
        output_image_folder.mkdir()

    # generate image
    image_generator.run_image_generation()
    image_random_name = str(uuid.uuid4())[:8]
    image_store_path = image_generator.save_image(output_image_folder, f"{image_random_name}.png")

    logger.info(f"Image stored at: {image_store_path}")
    
    # bind material and texture
    stage = omni.usd.get_context().get_stage()
    mtl_random_name = str(uuid.uuid4())[:3]
    mtl_path = Sdf.Path(f"/World/Looks/GenAI_OmniPBR_{mtl_random_name}")
    mtl = UsdShade.Material.Define(stage, mtl_path)
    shader = UsdShade.Shader.Define(stage, mtl_path.AppendPath("Shader"))
    shader.CreateImplementationSourceAttr(UsdShade.Tokens.sourceAsset)
    shader.SetSourceAsset("OmniPBR.mdl", "mdl")
    shader.SetSourceAssetSubIdentifier("OmniPBR", "mdl")
    mtl.CreateSurfaceOutput("mdl").ConnectToSource(shader.ConnectableAPI(), "out")
    mtl.CreateDisplacementOutput("mdl").ConnectToSource(shader.ConnectableAPI(), "out")
    mtl.CreateVolumeOutput("mdl").ConnectToSource(shader.ConnectableAPI(), "out")

    # set the texture
    diffuse_texture_in = shader.CreateInput("diffuse_texture", Sdf.ValueTypeNames.Asset)
    diffuse_texture_in.Set(str(image_store_path))
    diffuse_texture_in.GetAttr().SetColorSpace("sRGB")

    # bind the material to the prim
    UsdShade.MaterialBindingAPI(stage.GetPrimAtPath(prim_path)).Bind(mtl, UsdShade.Tokens.strongerThanDescendants)

    

#Not really too sure about this one
class materialAndTexture:
    def createMaterialAndTexture(material):
        material = UsdShade.Material.Define(stage, material)  #define material
        pbrShader = UsdShade.Shader.Define(stage, '/TexModel/boardMat/PBRShader')
        pbrShader.CreateIdAttr("UsdPreviewSurface")
        pbrShader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.4)
        pbrShader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)

        material.CreateSurfaceOutput().ConnectToSource(pbrShader.ConnectableAPI(), "surface")