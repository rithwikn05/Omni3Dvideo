import omni.kit.commands
from pxr import Usd, Sdf, Gf, UsdGeom


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
    stage.DefinePrim(prim_path)
    stage.DefinePrim("/camera", "Camera")
    prim_path_object = stage.GetPrimAtPath(prim_path)
    
    if "." in attribute_path:
        prim_attr_path, attr_path_and_component = attribute_path.split(".")
        if "|" in attr_path_and_component:
            attr_path, attr_component = attr_path_and_component.split("|")
    
    attribute = prim_path_object.GetAttribute(attr_path)   #This line is not working properly. For some reason the attribute type is not being transfered correctly

    if attr_component:
        current_value = attribute.Get(Usd.TimeCode(time))
        if current_value is None:
            current_value = Gf.Vec3f(0, 0, 0)
        
        if attr_component == "x":
            current_value[0] = value
        elif attr_component == "y":
            current_value[1] = value
        elif attr_component == "z":
            current_value[2] = value
        
        value = current_value

    start_position = Gf.Vec3f(0.0, 0.0, 0.0)
    attribute.Set(0, start_position)
    attribute.Set(value, Usd.TimeCode(time))
    
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

    
def create_rotation_animation(prim_path: str, duration: float, axis: str = "Y", degree: float = 360) -> None:
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

    xformable_prim = UsdGeom.Xformable(prim_object)
    xformable_prim.SetXformOpOrder([])

    if axis == "X":
        rotate_op = xformable_prim.AddRotateXOp(opSuffix='spin')
    elif axis == "Y":
        rotate_op = xformable_prim.AddRotateYOp(opSuffix='spin')
    elif axis == "Z":
        rotate_op = xformable_prim.AddRotateZOp(opSuffix='spin')
    
    rotate_op.Set(0, 0)
    rotate_op.Set(degree, duration)

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

    scale_op.GetAttributeSpline().SetInterpolation(UsdGeom.Tokens.linear)

    # stage = omni.usd.get_context().get_stage()
    # prim_object = stage.GetPrimAtPath(prim_path)

    # attribute = prim_object.GetAttribute("xform:scale").Get()
    # rotation_vector = Gf.Vec3f(0.0, 0.0, 0.0)

    # if axis == "X":
    #     rotation_vector[0] = degree
    # elif axis == "Y":
    #     rotation_vector[1] = degree
    # elif axis == "Z":
    #     rotation_vector[2] = degree

    # attribute.Set(rotation_vector, Usd.TimeCode(duration))