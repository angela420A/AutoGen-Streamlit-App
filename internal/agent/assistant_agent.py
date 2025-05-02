from io import BytesIO

import PIL
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import MultiModalMessage, StructuredMessage, TextMessage
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken, Image
from dotenv import load_dotenv

from internal.agent.memory import Memory

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

    async def response_memory_testing(self, new_message: str):
        msg = [TextMessage(content=new_message, source="user")]

        response = await self.agent.on_messages(
            msg, cancellation_token=CancellationToken()
        )
        yield response.chat_message.content
