#imports
from pxr import Usd    

def load_stage(self, name:str):
    self.stage = Usd.Stage.Open(name) #This is the stage object from which we can add prims to the stage
    self.stage.Save()
def save_stage_as(self, name:str):
    Usd.Stage.Save(name)     #Loads the stage to the specified file path