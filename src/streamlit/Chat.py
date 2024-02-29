import json

from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

import anamnesis_structure

st.set_page_config(
    page_title="Patient simulator",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'mailto:daniel.reichenpfader@bfh.ch',
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)
client = None
st.title("Simulating Diverse Patient Populations Using Patient Vignettes and Large Language Models")
if "vignette" not in st.session_state:
    st.session_state.vignette = ""
    with open ("data/input/vignette.json") as f:
        list = json.load(f)["vignette"]
        for dic in list:
            for key, val in dic.items():
                key = key.replace("_", " ")
                st.session_state.vignette += f"{key}: {val}\n\n"

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.session_state.openai_key = st.text_input("OpenAI key", type="password")
    st.session_state.openai_model = st.selectbox("OpenAI model", ["gpt-3.5-turbo", "gpt-4"], index=1)
    st.download_button(label="Download conversation history", data=json.dumps(st.session_state.messages), file_name="conversation_history.json", mime="application/json")

    if st.button("Reset chat"):
        st.session_state.messages = []
        st.toast("Chat was reset",icon= "👍")

    st.divider()
    st.markdown(anamnesis_structure.anamnesis_structure)

if st.session_state.openai_key:
    try:
        client = OpenAI(api_key=st.session_state.openai_key)
        client.models.list()
    except Exception as e:
        st.error(f"Error: Incorrect API key. Check the key and try again.")
    else:
        st.toast("OpenAI API key is valid")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask anamnesis question"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            history = [{"role": m["role"], "content": m["content"]}
                       for m in st.session_state.messages
                       ]
            history.insert(0, {"role": "system", "content": st.session_state.vignette})
            with st.chat_message("assistant"):
                stream = client.chat.completions.create(
                    seed=42,
                    model=st.session_state["openai_model"],
                    messages=history,
                    stream=True,
                )
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.warning("Please enter your OpenAI key in the sidebar to start the chat")
