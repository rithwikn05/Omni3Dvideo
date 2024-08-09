from pathlib import Path
from pxr import Usd, Sdf
import omni.usd


class createAssets:
    def __init__(self):
        self.stage = omni.usd.get_context().get_stage()
    #Creating basic geometry
    def create_cube(self, name:str):
        """
        Creates a cube object and places it on the stage

        Args:
            name (str): Name of the cube prim
        """
        cube: Usd.Prim = self.stage.DefinePrim(name, "Cube")
        self.stage.Save()
        return cube

    def create_plane(self, name:str):
        """
        Creates a place object and places it on the stage

        Args:
            name (str): Name of the cube prim
        """
        self.stage.DefinePrim(name, "Plane")
        self.stage.Save()

    def create_sphere(self, name:str):
        """
        Creates a sphere object and places it on the stage

        Args:
            name (str): Name of the cube prim
        """
        sphere: Usd.Prim = self.stage.DefinePrim(name, "Sphere")
        self.stage.Save()
        return sphere

    def get_cube_from_prim_path(self, name:str):
        """
        Creates a cube object and places it on the stage

        Args:
            name (str): Name of the cube prim
        """
        cube: Usd.Prim = self.stage.DefinePrim(name, "Cube")   #Here we are using a cube object
        cube_path = cube.GetPath()   #Gets the path of the cube that we created above
        box: Usd.Prim = self.stage.GetPrimAthPath(cube_path)  #Get the prim at the specified path
        print(box)  #prints the prim object at the path that is specified

    #Importing assets
    def add_reference(self, name:str):
        """
        Imports assets from the specified location to the stage

        Args:
            name (str): Name of the cube prim
        """
        cube = self.stage.DefinePrim("/cube", "Cube")
        ref = Sdf.Reference(name, "/ReferencedPrim")  # Here ReferencedPrim would be the cube path
        cube.GetReference().AddReference(ref)

    def add_payload(self, name:str):
        """
        Adds the specified payload to to the stage. 

        Args:
            name (str): Name of the cube prim
        """
        cube = self.stage.DefinePrim("/cube", "Cube")
        payload = Sdf.Payload(name, "/ReferencedPrim")   # Here ReferencedPrim would be the cube path
        cube.GetPayload().AddPayload(payload)
        self.stage.Load("/cube")  #loading payload

    def unload(self, name:str):
        """
        Unloads a prim from the scene

        Args:
            name (str): Name of the cube prim
        """
        self.stage.Unload("/cube")  #Unloading payload