from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType
from autogen_ext.models.openai import OpenAIChatCompletionClient


class Memory:
    def __init__(self):
        self.memory = ListMemory()

        self.config()

    async def config(self):
        await self.memory.add(
            MemoryContent(
                content="Return a clear and well-structured sentence.",
                mime_type=MemoryMimeType.TEXT,
            )
        )
        await self.memory.add(
            MemoryContent(
                content="Respond only in English.", mime_type=MemoryMimeType.TEXT
            )
        )

    def get_memory(self):
        return self.memory

    async def add_memory(self, new_memory):
        await self.memory.add(
            MemoryContent(content=new_memory, mime_type=MemoryMimeType.TEXT)
        )
