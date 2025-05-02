import asyncio
from io import BytesIO

import PIL
import streamlit as st
from autogen_core import Image
from autogen_core.models import UserMessage

from internal.agent.assistant_agent import Agent
from internal.agent.testing_function import TestFunction
from internal.config.config import Config


# Help function to get or create the event loop
def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()
        raise ex  # Re-raise other RuntimeError


async def initialize_agent():
    config = Config("config.yaml")
    az_model_client = config.get_azure_model_client()
    agent_instance = Agent(az_model_client)
    await agent_instance.async_init()
    return agent_instance


async def get_momory_context():
    if st.session_state.agent is None:
        st.error("You don't have any agent initialized.")
        st.stop()
    context = await st.session_state.agent.agent._model_context.get_messages()
    yield context


st.title("Erhol Bot")

# Set values
default_values = {"agent": None, "messages": []}
for key, val in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = val

if st.session_state.agent is None:
    with st.spinner("Initializing Agent . . ."):
        try:
            loop = get_or_create_eventloop()
            st.session_state.agent = loop.run_until_complete(initialize_agent())
        except Exception as e:
            st.error(f"Fatal Error: Could not initialize agent: {e}")
            st.stop()

if st.session_state is None:
    st.error(
        f"Agent initialization failed after attempt. Please check logs or restart."
    )
    st.stop()


# --- UI and Chat Logic ---
if st.button("Get Momory Context"):
    st.write_stream(get_momory_context())


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.chat_message("user").markdown(prompt)

    with st.chat_message("assistant"):
        response = st.write_stream(
            st.session_state.agent.response_memory_testing(prompt)
        )

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": response})
