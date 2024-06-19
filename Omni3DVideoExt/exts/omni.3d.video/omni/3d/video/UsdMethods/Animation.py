import omni.kit.commands
from pxr import Usd


def keyframe(prim_path: str, attribute_path: str, time: float, value: float) -> None:
    """
    Keyframe an attribute of a prim at a time with a value

    Args:
        prim_path (str): the path of the prim to keyframe
        attribute (str): the attribute to keyframe
        time (float): the time to keyframe
        value (float): the value to keyframe
    """

        #    @example
        #     1.  SetAnimCurveKeys()                      # Set keys to the selected prim(s), at the current time, with the default value
        #     2.  SetAnimCurveKeys(paths=["/World/Cube"]) # Set xformable attribute keys (current time, default value) to /World/Cube
        #     3.  SetAnimCurveKeys(paths=["/World/Cube.xformOp:scale|x"])
        #                                                 # Set a key (current time, default value) to the attribute /World/Cube.xformOp:scale|x
        #     4.  SetAnimCurveKeys(paths=["/World/Cube", "/World/Cube.xformOp:scale|x"])
        #                                                 # The same as executing both 2. and 3.
        #     5.  SetAnimCurveKeys(paths=["/World/Cube.xformOp:scale|x"], value=2.0, time=Usd.TimeCode(50))
        #                                                 # Set a key (50, 2.0) to the attribute /World/Cube.xformOp:scale|x
        #     6.  SetAnimCurveKeys(paths=["/World/Cube.xformOp:scale|x", "/World/Cube.xformOp:translate|x"], value=[0.0, 3.14, 2.0], time=[0, 30, 60], preserveCurveShape=False)
                                                        # Set keys (0, 0.0), (30, 3.14), and (60, 2.0) to the two given curves. preserveCurveShape must be set to `False`

    (result, err) = omni.kit.commands.execute("SetAnimCurveKeys",
            paths=[f"{attribute_path}"],
            value = value,
            time=Usd.TimeCode(time)
            )
    
def create_movement_animation(prim_path: str, duration: float, direction: str = "X", distance: float = 100.0) -> None:
    """
    Create a movement animation for a prim

    Args:
        prim_path (str): the path of the prim to animate
        duration (float): the duration of the animation
        direction (str): the direction to move
        distance (float): the distance to move
    """

    
def create_rotation_animation(prim_path: str, duration: float, axis: str = "Y", degree: float = 360) -> None:
    """
    Create a 360 degree rotation animation for a prim

    Args:
        prim_path (str): the path of the prim to animate
        duration (float): the duration of the animation
        axis (str): the axis to rotate
    """

def create_scale_animation(prim_path: str, duration: float, scale_ratio: float = 2.0) -> None:
    """
    Create a scale animation for a prim

    Args:
        prim_path (str): the path of the prim to animate
        duration (float): the duration of the animation
        scale_ratio (float): the scale ratio
    """