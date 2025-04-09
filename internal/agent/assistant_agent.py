from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import StructuredMessage, TextMessage
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
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

    async def assistant_run(self) -> None:
        response = await self.agent.on_messages(
            [TextMessage(
                content="What is the capital of Taiwan? Cloud you interduce the city?", source="user")],
            cancellation_token=CancellationToken(),
        )
        print(response)

    async def assistant_run_stream(self) -> None:
        await Console(
            self.agent.on_messages_stream(
                [TextMessage(
                    content="Find information on AutoGen", source="user")],
                cancellation_token=CancellationToken(),
            ),
            output_stats=True,  # Enable stats printing.
        )

    async def get_stream_response(self, messages):
        async for message in self.agent.on_messages_stream(
            [TextMessage(
                content=messages, source="user")],
            cancellation_token=CancellationToken(),
        ):
            if isinstance(message, Response):
                yield message.chat_message.content
            elif hasattr(message, 'content'):
                yield message.content
