
import streamlit as st

st.title("Patient vignette")

st.session_state.vignette = st.text_area("Vignette", st.session_state.vignette, height=800)

with st.sidebar:
    st.write("This is a patient vignette. It is a description of a patient's medical history and current condition. It is used to simulate a patient in a conversation with a chatbot. You can edit the vignette directly in this field.")
