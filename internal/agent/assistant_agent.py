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

        self.assistant_agent()

    def assistant_agent(self):
        self.agent = AssistantAgent(
            name="assistant",
            model_client=self.model_client,
            memory=[self.memory.get_memory()],
            system_message="You ara an assistant that helps the user to find the information they need.",
        )

    async def get_memory_context(self):
        messages = await self.agent._model_context.get_messages()
        yield messages

    def set_history_messages(self, history: list):
        history_messages = []
        for h in history:
            history_messages.append(TextMessage(content=h["content"], source=h["role"]))
        return history_messages

    async def assistant_run(self) -> None:
        response = await self.agent.on_messages(
            [
                TextMessage(
                    content="What is the capital of Taiwan? Cloud you interduce the city?",
                    source="user",
                )
            ],
            cancellation_token=CancellationToken(),
        )
        print(response)

    async def assistant_run_stream(self, msg: str) -> None:
        await Console(
            self.agent.on_messages_stream(
                [TextMessage(content=msg, source="user")],
                cancellation_token=CancellationToken(),
            ),
            output_stats=True,  # Enable stats printing.
        )

    async def get_stream_response(
        self, sessiion: list, new_prompt: str, file_type: str, file_content: bytes
    ):
        history = self.set_history_messages(sessiion)

        if file_type == "Image":
            pil_image = PIL.Image.open(BytesIO(file_content))
            img = Image(pil_image)
            history.append(
                MultiModalMessage(
                    content=[
                        new_prompt,
                        img,
                    ],
                    source="user",
                )
            )
        else:
            history.append(TextMessage(content=new_prompt, source="user"))

        async for message in self.agent.on_messages_stream(
            history,
            cancellation_token=CancellationToken(),
        ):
            if isinstance(message, Response):
                yield message.chat_message.content
            elif hasattr(message, "content"):
                yield message.content
