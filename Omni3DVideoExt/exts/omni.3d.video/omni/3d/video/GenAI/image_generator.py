import requests
import base64
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ImageGenerator:
    def __init__(self) -> None:
        self._headers = None
        self._image_data_bytes = None
        self._payload = None
        self._api_key = None
        self._invoke_url = None
        self._response = None

    def convert_base64_to_image(self) -> None:
        """
        Convert base64 reponse to image bytes
        """
        self._image_data_bytes = self._response["artifacts"][0]["base64"].encode("utf-8")

    def save_image(self, folder_path: str, image_name: str):
        """
        Save image to a folder
        """
        image_path = Path(folder_path) / image_name
        self.convert_base64_to_image()
        with open(image_path, "wb") as f:
            f.write(base64.decodebytes(self._image_data_bytes))

        return image_path
    
    def set_api_key(self, api_key: str) -> None:
        """
        Set the api key
        """
        self._api_key = api_key

    def set_invoke_url(self, invoke_url: str) -> None:
        """
        Set the invoke url
        """
        self._invoke_url = invoke_url

    def set_headers(self) -> None:
        """
        Set the headers
        """
        self._headers = {
            "authorization": "Bearer " + self._api_key,
            "accept": "application/json",
            "content-type": "application/json",
        }

    def set_payload(self, prompt: str = "a car"):
        """
        Set the payload
        """
        self._payload = {
            "height": 1024,
            "width": 1024,
            "text_prompts":[
                {
                    "weight": 1,
                    "text": prompt
                }
            ],
            "cfg_scale": 5,
            "clip_guidance_preset": "NONE",
            "sampler": "K_DPM_2_ANCESTRAL",
            "samples": 1,
            "seed": 0,
            "steps": 25,
            "style_preset": "none",
        }

    def run_image_generation(self):
        logger.info("Running image generation")
        response = requests.post(self._invoke_url, headers=self._headers, json=self._payload)

        response.raise_for_status()
        self._response = response.json()
        logger.info(f"Image generation complete: {self._response}")