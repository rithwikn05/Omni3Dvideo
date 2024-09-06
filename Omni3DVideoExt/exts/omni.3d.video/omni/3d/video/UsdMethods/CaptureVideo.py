import omni.ui
from omni.kit.widget.viewport import ViewportWidget
import omni.kit.capture.viewport
import omni.timeline
import carb
import os
from datetime import datetime

def setup_viewport():
    # Set up the viewport
    viewport_window = omni.ui.Window('SimpleViewport', width=1280, height=720+20)  # Add 20 for the title-bar
    with viewport_window.frame:
        viewport_widget = ViewportWidget(resolution=(1280, 720))

    # Control of the ViewportTexture happens through the object held in the viewport_api property
    viewport_api = viewport_widget.viewport_api

    # Set the resolution for the render
    viewport_api.resolution = (1280, 720)  # You can adjust this as needed

    # Set the camera path
    viewport_api.camera_path = '/camera'  # Adjust this to match your scene's camera path
    return viewport_api

def render_video(viewport_api, output_folder):
    print("[viewport task] start capture")
    
    os.makedirs(output_folder, exist_ok=True)

    options = omni.kit.capture.viewport.CaptureOptions()
    options.file_type = ".mp4"

    # Get the timeline
    timeline = omni.timeline.get_timeline_interface()
    
    # Set the start and end frames based on the existing timeline
    options.start_frame = int(timeline.get_start_time())
    options.end_frame = int(timeline.get_end_time())

    print(f"Capturing from frame {options.start_frame} to {options.end_frame}")

    # Clean up existing mp4 files
    for file in os.listdir(output_folder):
        if file.endswith(".mp4"):
            os.remove(os.path.join(output_folder, file))

    options.output_folder = str(output_folder)

    now = datetime.now()
    date_time = now.strftime("%m_%d_%Y_%H_%M_%S")
    video_path = os.path.join(options.output_folder, f"capture_{date_time}")
    carb.log_info(f"Capture video path: {video_path}")
    options.file_name = video_path

    # print(f"Saving video to: {video_path}.mp4")

    # Get render mode
    settings = carb.settings.get_settings()
    render_mode = settings.get("/rtx/rendermode")
    if render_mode == "PathTracing":
        options.render_preset = omni.kit.capture.viewport.CaptureRenderPreset.PATH_TRACE
    else:  # Assume RaytracedLighting
        options.render_preset = omni.kit.capture.viewport.CaptureRenderPreset.RAY_TRACE

    # Use the viewport we created
    options.viewport = viewport_api

    # Set up video capture settings
    options.capture_frames = True
    options.write_frames = True
    options.fps = timeline.get_time_codes_per_seconds()

    print(f"Capture frames: {options.capture_frames}")
    print(f"Write frames: {options.write_frames}")
    print(f"Frames per second: {options.fps}")

    # Start capture
    capture_instance = omni.kit.capture.viewport.CaptureExtension().get_instance()
    capture_instance.options = options
    capture_instance.start()

    capture_filename = f"{video_path}.mp4"
    
    return capture_filename

# Don't forget to destroy the objects when done with them
# viewport_widget.destroy()
# viewport_window.destroy()
# viewport_window, viewport_widget = None, None