import json
import os

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
path_to_json_files = "data/input/"
st.title("Simulating Diverse Patient Populations Using Patient Vignettes and Large Language Models")
if "vignettes" not in st.session_state:
    st.session_state.vignettes = []
    json_file_names = [filename for filename in os.listdir(path_to_json_files) if filename.endswith('.json')]
    for json_file_name in json_file_names:
        with open(os.path.join(path_to_json_files, json_file_name)) as json_file:
            vignette = ""
            list = json.load(json_file)["vignette"]
            for dic in list:
                for key, val in dic.items():
                    key = key.replace("_", " ")
                    vignette += f"{key}: {val}\n\n"
            st.session_state.vignettes.append([json_file_name, vignette])

if "current_vignette" not in st.session_state:
    st.session_state.current_vignette = st.session_state.vignettes[0]

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "user", "content": "Hello! I am Dr. Wenger and I will ask you several questions regarding your health now. Why are you here today?"},
                               {"role": "assistant", "content": "Thank you doctor for having me. I don't feel well and I have some symptoms that I would like to discuss with you."}]


with st.sidebar:
    st.session_state.openai_key = st.text_input("OpenAI key", type="password")
    st.session_state.openai_model = st.selectbox("OpenAI model", ["gpt-3.5-turbo", "gpt-4"], index=1)
    st.download_button(label="Download conversation history", data=json.dumps(st.session_state.messages), file_name="conversation_history.json", mime="application/json")

    if st.button("Reset chat"):
        st.session_state.messages = [{"role": "user",
                                      "content": "Hello! I am Dr. Lehmann and I will ask you several questions regarding your health now. Why are you here today?"},
                                     {"role": "assistant",
                                      "content": "Thank you doctor for having me. I don't feel well and I have some symptoms that I would like to discuss with you."}]

        st.toast("Chat was reset",icon= "👍")
    st.divider()
    st.markdown(anamnesis_structure.anamnesis_structure)
    st.divider()
    st.session_state.current_vignette = st.selectbox("Vignette", st.session_state.vignettes, format_func=lambda x: x[0])
    st.write(
        "You can edit the vignette directly in the field below. As the changes will be applied immediately, it is recommended to reset the chat history and start a new chat.")
    new_vignette = st.text_area("Vignette", st.session_state.current_vignette[1], height=800)
    if st.button("Save new vignette"):
        if new_vignette == st.session_state.current_vignette[1]:
            st.warning("The new vignette is the same as the old one. No changes were saved.")
        else:
            vignette_title = st.session_state.current_vignette[0] + "_edited"
            st.session_state.vignettes.append([vignette_title, new_vignette])

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
            history.insert(0,{"role": "system", "content": st.session_state.current_vignette[1]})
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




