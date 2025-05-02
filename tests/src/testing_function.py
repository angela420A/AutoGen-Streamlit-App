from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import MultiModalMessage, StructuredMessage, TextMessage
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken, Image

from utils import Memory


class TestFunction:
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
