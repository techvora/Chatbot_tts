import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()


class AvatarManager:
    def __init__(self):
        self.API_KEY = os.getenv("HEYGEN_API_KEY")

    def upload_image(self, image_file):
        """
        https://docs.heygen.com/reference/upload-talking-photo
        :param image_file:
        :return:
        """
        headers = {
            "x-api-key": self.API_KEY,
            "Content-Type": image_file.type
        }

        print(headers)

        response = requests.post("https://upload.heygen.com/v1/talking_photo", headers=headers, data=image_file.getvalue())

        if response.status_code == 200:
            print("Uploaded image id :-", response.json().get("data", {}).get("talking_photo_id"))
            return response.json().get("data", {}).get("talking_photo_id")
        else:
            return f"Image upload failed: {response.text}"

    def get_voice_id(self, locale="en-IN"):
        """
        function that can fetch voice id
        :param locale: default pass "en-IN"
        :return:
        """

        headers = {
            "x-api-key": self.API_KEY
        }

        response = requests.get("https://api.heygen.com/v2/voices", headers=headers)

        if response.status_code == 200:
            json_data = response.json()
            data = json_data.get("data", {})

            # Check if 'data' is a dictionary and contains 'voices'
            if isinstance(data, dict) and "voices" in data:
                voices = data["voices"]
            elif isinstance(data, list):
                voices = data  # In case data itself is a list of voices
            else:
                return "Unexpected data format."

            for voice in voices:
                if voice.get("locale") == locale:
                    return voice.get("voice_id")

            # Fallback to first voice_id if no locale match
            return voices[0].get("voice_id") if voices else None

        else:
            return f"Failed to retrieve voices: {response.text}"

    def generate_video(self, talking_photo_id, script_text, voice_id):
        """
        https://docs.heygen.com/reference/create-an-avatar-video-v2
        :param talking_photo_id:
        :param script_text:
        :param voice_id:
        :return: video_id
        """

        headers = {
            "x-api-key": self.API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "video_inputs": [
                {
                    "character": {
                        "type": "talking_photo",
                        "talking_photo_id": talking_photo_id
                    },
                    "voice": {
                        "type": "text",
                        "input_text": script_text,
                        "voice_id": voice_id
                    }
                }
            ],
            "dimension": {
                "width": 720,
                "height": 1280
            }
        }
        response = requests.post("https://api.heygen.com/v2/video/generate", headers=headers, json=payload)
        if response.status_code == 200:
            return response.json().get("data", {}).get("video_id")
        else:
            return f"Video generation failed: {response.text}"

    def get_video_url(self, video_id):
        """
        https://docs.heygen.com/reference/create-an-avatar-video-v2
        :param video_id: it take script based generated video id
        :return: generated video url
        """
        headers = {
            "x-api-key": self.API_KEY
        }
        print(video_id)
        print(headers)
        video_status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"

        max_retries = 15  # Poll for up to 60 seconds
        for attempt in range(max_retries):
            try:
                response = requests.get(video_status_url, headers=headers)

                if response.status_code == 200:
                    data = response.json().get("data", {})
                    status = data.get("status")

                    if status == "completed":
                        return data.get("video_url")
                    elif status == "failed":
                        return "Video generation failed."
                    else:
                        # Still processing
                        time.sleep(5)  # Wait before next poll
                else:
                    print(f"Unexpected response: {response.status_code} - {response.text}")
                    time.sleep(2)
            except requests.exceptions.RequestException as e:
                print(f"Retry {attempt + 1}/{max_retries} - Connection error: {e}")
                time.sleep(2)

        return "Video generation is taking longer than expected. Please try again later."

    def get_avatar(self):
        """
        :return: list of avatars including default and your own avatar
        """

        headers = {
            "accept": "application/json",
            "x-api-key": self.API_KEY
        }

        response = requests.get("https://api.heygen.com/v2/avatars", headers=headers)
        return response.json().get("data", {})
