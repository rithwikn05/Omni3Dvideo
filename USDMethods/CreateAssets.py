from pathlib import Path
from pxr import Usd, Sdf

layer_path = str(Path.home() / "defining_prims.usda")
stage = Usd.Stage.CreateNew(layer_path)

class createAssets:
    #Creating basic geometry
    def create_cube(str):
        stage.DefinePrim(str, "Cube")
        stage.Save()

    def create_plane(str):
        stage.DefinePrim(str, "Plane")
        stage.Save()

    def create_sphere(str):
        stage.DefinePrim(str, "Sphere")
        stage.Save()

    def get_cube_from_prim_path():  #General example for how we can get prim from path
        cube: Usd.Prim = stage.DefinePrim(str, "Cube")   #Here we are using a cube object
        cube_path = cube.GetPath()   #Gets the path of the cube that we created above
        box: Usd.Prim = stage.GetPrimAthPath(cube_path)  #Get the prim at the specified path
        print(box)  #prints the prim object at the path that is specified

    #Importing assets
    def add_reference(str):
        cube = stage.DefinePrim("/cube", "Cube")
        ref = Sdf.Reference(str, "/ReferencedPrim")  # Here ReferencedPrim would be the cube path
        cube.GetReference().AddReference(ref)

    def add_payload(str):
        cube = stage.DefinePrim("/cube", "Cube")
        payload = Sdf.Payload(str, "/ReferencedPrim")   # Here ReferencedPrim would be the cube path
        cube.GetPayload().AddPayload(payload)
        stage.Load("/cube")  #loading payload

    def unload(str):
        stage.Unload("/cube")  #Unloading payload
