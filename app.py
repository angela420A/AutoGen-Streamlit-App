import asyncio
from io import BytesIO

import PIL
import streamlit as st
from autogen_core import Image
from autogen_core.models import UserMessage

from internal.agent.assistant_agent import Agent
from internal.config.config import Config

config = Config("config.yaml")
az_model_client = config.get_azure_model_client()
agent = Agent(az_model_client)

st.title("Erhol Bot")

st.session_state._file_type = None
st.session_state._update_logger = None
st.session_state._bytes_data = None

if "messages" not in st.session_state:
    st.session_state.messages = []

file_type = st.radio(
    "Select the type of file you want to upload",
    # ["Image", "PDF", "None"],
    ["Image", "None"],
    index=None,
)

# if file_type == "PDF" or file_type == "Image":
if file_type == "Image":
    st.session_state._file_type = file_type
    st.session_state._update_logger = st.file_uploader(
        "Choose only jpg, png of pdf file",
        # type=["jpg", "png", "pdf"],
        type=["jpg", "png"],
    )
else:
    st.session_state._file_type = None
    st.session_state._update_logger = None

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.chat_message("user").markdown(prompt)
    # st.session_state.messages.append({"role": "user", "content": prompt})

    if st.session_state._update_logger is not None:
        st.session_state._bytes_data = st.session_state._update_logger.getvalue()
        # if st.session_state._file_type == "Image":
        #     image = PIL.Image.open(BytesIO(bytes_data))
        #     img = Image(image)
        #     st.session_state.messages.append({"role": "user", "content": img})
        # if st.session_state._file_type == "PDF":
        #     pdf = BytesIO(bytes_data)

    with st.chat_message("assistant"):
        response = st.write_stream(
            agent.get_stream_response(
                st.session_state.messages,
                prompt,
                st.session_state._file_type,
                st.session_state._bytes_data,
            )
        )

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": response})

    # if __name__ == "__main__":
    #     config = Config("config.yaml")
    #     az_model_client = config.get_azure_model_client()
    #     agent = Agent(az_model_client)
    #     asyncio.run(agent.assistant_run_stream("What is the capital of Taiwan?"))

    #     async def consume_memory_context():
    #         async for context in agent.get_memory_context():
    #             print(context)

    #     asyncio.run(consume_memory_context())
