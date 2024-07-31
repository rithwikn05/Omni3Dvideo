from pathlib import Path
from pxr import Usd, Sdf
import omni.usd


class createAssets:
    def __init__(self):
        self.stage = omni.usd.get_context().get_stage()
    #Creating basic geometry
    def create_cube(self, name:str):
        cube: Usd.Prim = self.stage.DefinePrim(name, "Cube")
        self.stage.Save()
        return cube

    def create_plane(self, name:str):
        self.stage.DefinePrim(name, "Plane")
        self.stage.Save()

    def create_sphere(self, name:str):
        sphere: Usd.Prim = self.stage.DefinePrim(name, "Sphere")
        self.stage.Save()
        return sphere

    def get_cube_from_prim_path(self, name:str):  #General example for how we can get prim from path
        cube: Usd.Prim = self.stage.DefinePrim(name, "Cube")   #Here we are using a cube object
        cube_path = cube.GetPath()   #Gets the path of the cube that we created above
        box: Usd.Prim = self.stage.GetPrimAthPath(cube_path)  #Get the prim at the specified path
        print(box)  #prints the prim object at the path that is specified

    #Importing assets
    def add_reference(self, name:str):
        cube = self.stage.DefinePrim("/cube", "Cube")
        ref = Sdf.Reference(name, "/ReferencedPrim")  # Here ReferencedPrim would be the cube path
        cube.GetReference().AddReference(ref)

    def add_payload(self, name:str):
        cube = self.stage.DefinePrim("/cube", "Cube")
        payload = Sdf.Payload(name, "/ReferencedPrim")   # Here ReferencedPrim would be the cube path
        cube.GetPayload().AddPayload(payload)
        self.stage.Load("/cube")  #loading payload

    def unload(self, name:str):
        self.stage.Unload("/cube")  #Unloading payload