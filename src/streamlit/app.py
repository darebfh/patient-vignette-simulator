import json

from openai import OpenAI
import streamlit as st

import anamnesis_structure

st.title("Simulating Diverse Patient Populations Using Patient Vignettes and Large Language Models")


#client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
client = OpenAI()

patient_vignette = ""
with open ("data/input/vignette.json") as f:
    list = json.load(f)["vignette"]
    for dic in list:
        for key, val in dic.items():
            patient_vignette += f"{val}\n"

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4"

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    if st.download_button(label="Download conversation history and reset chat", data=json.dumps(st.session_state.messages), file_name="conversation_history.json", mime="application/json"):
        st.session_state.messages = []

    st.divider()
    st.markdown(anamnesis_structure.anamnesis_structure)

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
    history.insert(0, {"role": "system", "content": patient_vignette})
    print(history)
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=history,
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})