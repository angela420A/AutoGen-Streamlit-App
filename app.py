import asyncio
from io import BytesIO

import PIL
import streamlit as st
from autogen_core import Image
from autogen_core.models import UserMessage

from src.agent.assistant_agent import Agent
from tests.src.testing_function import TestFunction
from utils import Config


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


st.title("AutoGen-Streamlit-AgentChat")

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

if st.session_state.agent is None:
    st.error(
        f"Agent initialization failed after attempt. Please check logs or restart."
    )
    st.stop()

# --- UI and Chat Logic ---

if st.button("Get Momory Context"):
    st.write_stream(get_momory_context())

option_map = {0: ":material/image:", 1: ":material/description:", 2: ":material/close:"}
selection = st.pills(
    "Select the file type to upload",
    options=option_map.keys(),
    format_func=lambda option: option_map[option],
    selection_mode="single",
)

if selection == 0:
    uploaded_files = st.file_uploader(
        "Choose a image file", accept_multiple_files=True, type=["jpg", "jpeg", "png"]
    )
elif selection == 1:
    uploaded_files = st.file_uploader(
        "Choose a pdf file", accept_multiple_files=False, type="pdf"
    )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.chat_message("user").markdown(prompt)

    if selection == 0:
        imgs_byte_data = []
        for img in uploaded_files:
            imgs_byte_data.append(img.getvalue())

        with st.chat_message("assistant"):
            response = st.write_stream(
                st.session_state.agent.generate_response_with_images(
                    prompt, imgs_byte_data
                )
            )
    else:
        with st.chat_message("assistant"):
            response = st.write_stream(st.session_state.agent.generate_response(prompt))

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": response})
