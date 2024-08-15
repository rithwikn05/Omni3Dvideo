import omni.kit.commands
from pxr import Usd, Sdf, Gf, UsdGeom
import math


def keyframe(prim_path: str, attribute_path: str, time: float, value: float) -> None:
    """
    Keyframe an attribute of a prim at a time with a value

    Args:
        prim_path (str): the path of the prim to keyframe
        attribute (str): the attribute to keyframe
        time (float): the time to keyframe
        value (float): the value to keyframe
    """
    stage = omni.usd.get_context().get_stage()
    stage.DefinePrim(prim_path, "Cube")

    # Get the prim
    prim = stage.GetPrimAtPath(prim_path)
    if not prim.IsValid():
        raise ValueError(f"Prim not found at path: {prim_path}")
    
    if "." in attribute_path:
        prim_attr_path, attr_path_and_component = attribute_path.split(".")
        # print("attr_path_and_component: ", attr_path_and_component)
        if "|" in attr_path_and_component:
            attr_path, attr_component = attr_path_and_component.split("|")  #attr_path: "xformOp:translate"
            # print("attr_path:", attr_path)
            # print("attr_component: ", attr_component)

    print("attr_path:", attr_path)
     # Ensure the prim is a Xformable
    xformable = UsdGeom.Xformable(prim)

    if not "xformOp:translate" in prim.GetAttributes:
        xformable = xformable.AddTranslateOp()
    if not "xformOp:rotate" in prim.GetAttributes: 
        xformable = xformable.AddRotateXYZOp()
    if not "xformOp:scale" in prim.GetAttributes: 
        xformable = xformable.AddScaleOp()

    # # Add transform operations if they don't exist
    # if attr_path == "xformOp:translate":
    #     xformable = xformable.AddTranslateOp()
    # elif attr_path == "xformOp:rotate":
    #     xformable = xformable.AddRotateXYZOp()
    # elif attr_path == "xformOp:scale":
    #     xformable = xformable.AddScaleOp()
    
    
    print(attr_path_and_component)
    attribute_path = prim_attr_path + "." + attr_path

    # Get the attribute using the full attribute path
    xformable = stage.GetAttributeAtPath(attribute_path)
    if not xformable:
        print(f"Available attributes for {prim_path}:")
        for attr in prim.GetAttributes():
            print(f"  {attr.GetName()}")
        raise ValueError(f"Attribute not found: {attribute_path} on prim {prim_path}")
    
    current_value = Gf.Vec3f(value, value, value)

    # Set the keyframe
    xformable.Set(current_value, Usd.TimeCode(time))

    # xformable.SetXformOpOrder([])
    
def create_movement_animation(prim_path: str, duration: float, direction: str = "X", distance: float = 2000.0) -> None:
    """
    Create a movement animation for a prim

    Args:
        prim_path (str): the path of the prim to animate
        duration (float): the duration of the animation
        direction (str): the direction to move
        distance (float): the distance to move
    """
    stage = omni.usd.get_context().get_stage()
    stage.DefinePrim(prim_path, "Cube")
    prim_object = stage.GetPrimAtPath(prim_path)

    xformable_object = UsdGeom.Xformable(prim_object)
    xformable_object.SetXformOpOrder([])
    xformable_object = xformable_object.AddTranslateOp()

    # Create or get the translate operation
    translate_attr = prim_object.GetAttribute("xformOp:translate").Get()

    start_position = Gf.Vec3f(0.0, 0.0, 0.0)
    end_position = Gf.Vec3f(start_position)
    if direction == "X":
        end_position[0] += distance
    elif direction == "Y":
        end_position[1] += distance
    elif direction == "Z":
        end_position[2] += distance

    xformable_object.Set(start_position, 0)
    xformable_object.Set(end_position, duration)

    
def create_rotation_animation(prim_path: str, duration: float, axis: str = "Y", degree: float = 180) -> None:
    """
    Create a 360 degree rotation animation for a prim

    Args:
        prim_path (str): the path of the prim to animate
        duration (float): the duration of the animation
        axis (str): the axis to rotate
    """
    stage = omni.usd.get_context().get_stage()
    stage.DefinePrim(prim_path, "Cube")
    prim_object = stage.GetPrimAtPath(prim_path)

    angle_in_radians = math.radians(degree) - math.radians(degree) * 2

    xformable_prim = UsdGeom.Xformable(prim_object)
    xformable_prim.SetXformOpOrder([])

    if axis.lower() == "x":
        axis = Gf.Vec3d(1, 0, 0).GetNormalized()
    elif axis.lower() == "y":
        axis = Gf.Vec3d(0, 1, 0).GetNormalized()
    elif axis.lower() == "z":
        axis = Gf.Vec3d(0, 0, 1).GetNormalized()
    
    new_angle = Gf.Quatf(math.cos(angle_in_radians / 2), axis[0] * math.sin(angle_in_radians / 2), axis[1] * math.sin(angle_in_radians / 2), axis[2] * math.sin(angle_in_radians / 2))
    xformable_prim = xformable_prim.AddOrientOp()
    
    xformable_prim.Set(Gf.Quatf(0.0, 0.0, 0.0, 0.0), 0)
    xformable_prim.Set(new_angle, duration)

def create_scale_animation(prim_path: str, duration: float, scale_ratio: float = 2.0) -> None:
    """
    Create a scale animation for a prim

    Args:
        prim_path (str): the path of the prim to animate
        duration (float): the duration of the animation
        scale_ratio (float): the scale ratio
    """

    stage = omni.usd.get_context().get_stage()
    stage.DefinePrim(prim_path, "Cube")
    prim_object = stage.GetPrimAtPath(prim_path)

    xformable_prim = UsdGeom.Xformable(prim_object)
    xformable_prim.SetXformOpOrder([])
    scale_op = xformable_prim.AddScaleOp(UsdGeom.XformOp.PrecisionFloat)

    start_scale = Gf.Vec3f(0.0, 0.0, 0.0)
    end_scale = Gf.Vec3f(scale_ratio, scale_ratio, scale_ratio)
    
    scale_op.Set(start_scale, 0)
    scale_op.Set(end_scale, duration)