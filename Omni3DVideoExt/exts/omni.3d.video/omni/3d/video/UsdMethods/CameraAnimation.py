from pxr import UsdGeom, Usd, Gf
import omni.usd

def camera_zoom_in(camera_path: str, zoom_ratio: float = 2.0, duration: float = 3):
    """
    Create a camera zoom in animation

    Args:
        camera_path (str): the path of the camera
        zoom_ratio (float): the ratio of the zoom
        duration (float): the duration of the animation in seoconds
    """
    stage = omni.usd.get_context().get_stage()
    camera = stage.GetPrimAtPath(camera_path)

    focal_length_attr = camera.GetAttribute("focalLength")
    current_focal_length = focal_length_attr.Get()
    new_focal_length = current_focal_length / zoom_ratio

    focal_length_attr.Set(value=current_focal_length, time=0)

    end_time = duration * stage.GetFramesPerSecond()
    focal_length_attr.Set(value=new_focal_length, time=end_time)


