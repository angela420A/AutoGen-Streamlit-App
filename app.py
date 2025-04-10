import asyncio

import streamlit as st
from autogen_core.models import UserMessage

from internal.agent.assistant_agent import Agent
from internal.config.config import Config

config = Config("config.yaml")
az_model_client = config.get_azure_model_client()
agent = Agent(az_model_client)

st.title("Erhol Bot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        response = st.write_stream(
            agent.get_stream_response(st.session_state.messages))

    st.session_state.messages.append(
        {"role": "assistant", "content": response})

    # if __name__ == "__main__":
    #     config = Config("config.yaml")
    #     az_model_client = config.get_azure_model_client()
    #     agent = Agent(az_model_client)
    #     asyncio.run(agent.assistant_run_stream("What is the capital of Taiwan?"))

    #     async def consume_memory_context():
    #         async for context in agent.get_memory_context():
    #             print(context)

    #     asyncio.run(consume_memory_context())
