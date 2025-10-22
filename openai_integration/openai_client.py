import os
from openai import OpenAI
import base64
from typing import List, Union
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()


class OpenAIClient:
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        """
        Initialize the OpenAI client.

        Args:
            api_key: OpenAI API key (if None, reads from OPENAI_API_KEY env variable)
            model: Model to use (default: gpt-4o, which supports vision)
        """
        self.chat = None
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set in OPENAI_API_KEY environment variable")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def send_message(self, message: str, system_prompt: str = None) -> str:
        """
        Send a text-only message to OpenAI.

        Args:
            message: The user message to send
            system_prompt: Optional system prompt to set context

        Returns:
            The assistant's response as a string
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": message})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )

        return response.choices[0].message.content

    def send_message_with_images(
            self,
            message: str,
            images: Union[str, Image.Image, List[Union[str, Image.Image]]],
            system_prompt: str = None
    ) -> str:
        """
        Send a message with one or more images to OpenAI.

        Args:
            message: The user message to send
            images: Can be:
                - A string (file path)
                - A PIL Image object
                - A list of strings (file paths) and/or PIL Image objects
            system_prompt: Optional system prompt to set context

        Returns:
            The assistant's response as a string
        """
        # Convert single image to list
        if isinstance(images, (str, Image.Image)):
            images = [images]

        # Build the content array with text and images
        content = [{"type": "text", "text": message}]

        for image in images:
            # Encode image (handles both file paths and PIL images)
            image_data, mime_type = self._process_image(image)

            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{image_data}"
                }
            })

        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": content})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )

        return response.choices[0].message.content

    def _process_image(self, image: Union[str, Image.Image]) -> tuple[str, str]:
        """
        Process an image (either file path or PIL Image) and return base64 encoding.

        Args:
            image: Either a file path (str) or PIL Image object

        Returns:
            Tuple of (base64_encoded_string, mime_type)
        """
        if isinstance(image, str):
            # It's a file path
            return self._encode_image_from_path(image)
        elif isinstance(image, Image.Image):
            # It's a PIL Image
            return self._encode_pil_image(image)
        else:
            raise ValueError(f"Unsupported image type: {type(image)}")

    def _encode_image_from_path(self, image_path: str) -> tuple[str, str]:
        """
        Encode an image file to base64.

        Args:
            image_path: Path to the image file

        Returns:
            Tuple of (base64_encoded_string, mime_type)
        """
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode('utf-8')

        # Determine MIME type from extension
        extension = image_path.lower().split('.')[-1]
        mime_type = self._get_mime_type(extension)

        return encoded, mime_type

    def _encode_pil_image(self, pil_image: Image.Image) -> tuple[str, str]:
        """
        Encode a PIL Image to base64.

        Args:
            pil_image: PIL Image object

        Returns:
            Tuple of (base64_encoded_string, mime_type)
        """
        # Convert to RGB if necessary (e.g., for RGBA or other modes)
        if pil_image.mode not in ('RGB', 'L'):
            pil_image = pil_image.convert('RGB')

        # Save to bytes buffer
        buffer = BytesIO()
        format_type = pil_image.format if pil_image.format else 'PNG'

        # Ensure format is supported
        if format_type not in ['PNG', 'JPEG', 'JPG', 'GIF', 'WEBP']:
            format_type = 'PNG'

        pil_image.save(buffer, format=format_type)
        encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')

        mime_type = self._get_mime_type(format_type.lower())

        return encoded, mime_type

    def _get_mime_type(self, extension: str) -> str:
        """
        Get MIME type from file extension.

        Args:
            extension: File extension (without dot)

        Returns:
            MIME type string
        """
        mime_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        return mime_types.get(extension.lower(), 'image/jpeg')
