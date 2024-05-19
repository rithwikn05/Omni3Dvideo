#imports
from pxr import Usd    

def load_stage(str):
    stage = Usd.Stage.Open(str) #This is the stage object from which we can add prims to the stage
def save_stage_as(str):
    Usd.Stage.Save(str)     #Loads the stage to the specified file path