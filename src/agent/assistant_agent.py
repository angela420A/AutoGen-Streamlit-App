from io import BytesIO

import PIL
import PIL.Image
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import MultiModalMessage, StructuredMessage, TextMessage
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken, Image
from dotenv import load_dotenv

from utils import Memory

load_dotenv()


class Agent:
    def __init__(self, model_client):
        self.model_client = model_client
        self.agent = None
        self.memory = Memory()
        self._initicalized = False

    async def async_init(self):
        if self._initicalized:
            return
        await self.memory.async_init()
        self._setup_assistant_agent()
        self._initicalized = True

    def _setup_assistant_agent(self):
        if self.agent is not None:
            return
        self.agent = AssistantAgent(
            name="assistant",
            model_client=self.model_client,
            memory=[self.memory.get_memory()],
            system_message="You ara an assistant that helps the user to find the information they need.",
        )

    async def generate_response(self, new_message: str):
        msg = [TextMessage(content=new_message, source="user")]

        response = await self.agent.on_messages(
            msg, cancellation_token=CancellationToken()
        )
        yield response.chat_message.content

    async def generate_response_with_images(
        self, new_messages: str, imgs_byte_data: list[bytes]
    ):
        contents = [new_messages]

        for img_byte_data in imgs_byte_data:
            pil_image = PIL.Image.open(BytesIO(img_byte_data))

            # Check if the image is in Palette mode and has transparency info in bytes
            # Pillow stores this info in the 'transparency' key of the info dict for P mode images
            if pil_image.mode == "P" and isinstance(
                pil_image.info.get("transparency"), bytes
            ):
                # Convert to RGBA to handle transparency explicitly
                pil_image = pil_image.convert("RGBA")

            img = Image(pil_image)
            contents.append(img)

        multi_msg = MultiModalMessage(content=contents, source="user")

        response = await self.agent.on_messages(
            [multi_msg], cancellation_token=CancellationToken()
        )
        yield response.chat_message.content
