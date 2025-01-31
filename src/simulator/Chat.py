import json
import os

from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

import anamnesis_structure

st.set_page_config(
    page_title="Patient:innen-Simulator",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'mailto:daniel.reichenpfader@bfh.ch',
        'About': "This source code © 2024 by K. Denecke and D. Reichenpfader is licensed under CC BY-SA 4.0"
    }
)
client = None
path_to_json_files = "data/input/"
st.title("Simulation diverser Patient*innen-Populationen mit Fallvignetten und Large Language Models")
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
    st.session_state.messages = [{"role": "user", "content": "Guten Tag! Mein Name ist Dr. Wenger und ich werde Sie nun zu Ihrem Gesundheitszustand befragen. Warum sind Sie heute hier?"},
                               {"role": "assistant", "content": "Vielen Dank Frau Doktor. Ich fühle mich aktuell nicht gut und habe ein paar Symptome, über die ich mit Ihnen reden möchte."}]


with st.sidebar:
    inserted_pw = st.text_input("Passwort eingeben und mit Enter bestätigen", type="password")
    st.session_state.openai_key = ""
    if inserted_pw.strip() == st.secrets["password"]:
        st.session_state.openai_key = st.secrets["openai_key"]
    elif inserted_pw.strip() != "":
        st.warning("Passwort inkorrekt.")

    st.session_state.openai_model = st.selectbox("Sprachmodell", ["gpt-4o-mini", "gpt-4o"], index=0)
    st.download_button(label="Konversation herunterladen", data=json.dumps(st.session_state.messages), file_name="conversation_history.json", mime="application/json")

    if st.button("Konversation zurücksetzen"):
        st.session_state.messages = [{"role": "user",
                                      "content": "Guten Tag! Mein Name ist Dr. Wenger und ich werde Sie nun zu Ihrem Gesundheitszustand befragen. Warum sind Sie heute hier?"},
                                     {"role": "assistant",
                                      "content": "Vielen Dank Frau Doktor. Ich fühle mich aktuell nicht gut und habe ein paar Symptome, über die ich mit Ihnen reden möchte."}]

        st.toast("Konversation wurde zurückgesetzt",icon= "👍")
    st.divider()
    with st.expander("Tipps zur Anamnese anzeigen"):
        st.markdown(anamnesis_structure.anamnesis_structure)
    with st.expander("Vignetten wechseln und bearbeiten"):
        st.session_state.current_vignette = st.selectbox("Vignette", st.session_state.vignettes, format_func=lambda x: x[0])
        st.write(
            "Du kannst die Vignette in folgendem Textfeld direkt anpassen. Da die Änderungen direkt angewendet werden, sollte die aktuelle Konversation gelöscht werden.")
        new_vignette = st.text_area("Vignette", st.session_state.current_vignette[1], height=800)
        if st.button("Neue Vignette speichern"):
            if new_vignette == st.session_state.current_vignette[1]:
                st.warning("Es wurden keine Änderungen erkannt.")
            else:
                vignette_title = st.session_state.current_vignette[0] + "_edited"
                st.session_state.vignettes.append([vignette_title, new_vignette])
    st.divider()
    if st.session_state.openai_key:
        st.text("Fertig mit der Anamnese? Du kannst mit folgendem Button deine Anamnese-Skills bewerten lassen. Schaffst du eine Bewertung von 100 Punkten?")
        if st.button("Anamnese bewerten"):
            with st.spinner("Bewertung der Anamnese läuft..."):
                try:
                    client = OpenAI(api_key=st.session_state.openai_key)
                    client.models.list()
                except Exception as e:
                    st.error(f"Achtung: API Schlüssel inkorrekt.  Überprüfe den Schlüssel und versuche es erneut.")
                else:
                    history = str([{"role": m["role"], "content": m["content"]}
                               for m in st.session_state.messages
                               ])
                    system_prompt = "Du bist eine erfahrene Hausärztin und unterrichtest Patient:innen-Kommunikation an einer medizinischen Universität. Bewerte, wie gut der Arzt bzw. die Ärztin folgendes simulierte Anamnese-Gespräch mit einem simulierten Patienten bzw. einer simulierten Patientin durchführt. Deine kritische Bewertung betrifft den Arzt bzw. die Ärztin und besteht aus einem Score zwischen 1 und 100 sowie einer kurzen Erklärung, was verbessert werden könnte. Für einen Score von 100 müssen alle Aspekte aus der Beschreibung erfragt werden. Erkläre ausserdem, welche Aspekte aus der Patientenbeschreibung übersehen wurden. Verewende Gender-gerechte Sprache. Verwende Markdown, um den Text zu formatieren. Beschreibung des Patienten: " + st.session_state.current_vignette[1]
                    messages = [
                        {"role": "developer", "content": system_prompt},
                        {
                            "role": "user",
                            "content": history
                        }
                    ]
                    response = client.chat.completions.create(
                        seed=42,
                        model=st.session_state["openai_model"],
                        messages=messages,
                        stream=False
                    )

                    st.markdown(response.choices[0].message.content)
                    with st.expander("Prompt anzeigen"):
                        st.code(messages, language="json", wrap_lines=True)
                    st.balloons()


if st.session_state.openai_key != "":
    try:
        client = OpenAI(api_key=st.session_state.openai_key)
        client.models.list()
    except Exception as e:
        st.error(f"Achtung: Passwort inkorrekt.  Überprüfe das Passwort und versuche es erneut.")
    else:
        st.toast("Passwort erfolgreich validiert", icon="🔑")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Stelle eine Frage"):
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
    st.warning("Gib das Passwort links oben in der Seitenleiste ein, um den Chat zu starten.")




