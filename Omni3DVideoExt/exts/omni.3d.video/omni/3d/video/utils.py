import sys
from os import path, getcwd, walk
from pathlib import Path
from json import loads
import logging
import omni.kit.app

logger = logging.getLogger(__name__)

def get_extension_path(extension_name: str = __name__) -> Path:
    """
    Get the path of an extension

    Args:
        extension_name (str): the name of the extension

    Returns:
        extension Path
    """
    manager = omni.kit.app.get_app().get_extension_manager()
    ext_id = manager.get_extension_id_by_module(extension_name)
    extension_path = manager.get_extension_path(ext_id)
    logger.info(f"Extension path: {extension_path}")
    return Path(extension_path)