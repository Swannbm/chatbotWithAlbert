import os

import requests
from dotenv import load_dotenv
import streamlit as st


load_dotenv()


class AlbertAPI:
    def __init__(self):
        self.api_key = os.getenv("APIKEY")
        self.base_url = os.getenv("APIROOT")
        self.version = os.getenv("APIVERSION")
        self.model = "mistralai/Pixtral-12B-2409"

        if not self.api_key or not self.base_url:
            raise ValueError("APIKEY, APIROOT ou APIVERSION manquant dans .env")

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def get_endpoint_url(self, endpoint):
        url = self.base_url
        if self.version:
            url = f"{url}/{self.version}"
        return f"{url}/{endpoint}"

    def send_question(self, messages):
        data = {
            "model": self.model,
            "messages": messages,
        }
        with st.spinner("Albert réfléchit..."):
            try:
                response = requests.post(
                    self.get_endpoint_url("chat/completions"),
                    headers=self.get_headers(),
                    json=data,
                )
                response.raise_for_status()
                result = response.json()
                if "choices" in result:
                    # direct call to AlberAPI
                    return result["choices"][0]["message"]["content"]
                return result["reply"]
            except requests.exceptions.RequestException as e:
                raise RuntimeError(
                    f"Erreur avec la requête : {e}, réponse : {response.text if 'response' in locals() else 'Aucune'}"
                )
    
    def send_rag(self, messages):
        data = {
            "messages": messages,
        }
        with st.spinner("Albert réfléchit..."):
            try:
                response = requests.post(
                    self.get_endpoint_url("rag/albert-source-code/"),
                    headers=self.get_headers(),
                    json=data,
                )
                response.raise_for_status()
                return response.json().get("reply")
            except requests.exceptions.RequestException as e:
                raise RuntimeError(
                    f"Erreur avec la requête : {e}, réponse : {response.text if 'response' in locals() else 'Aucune'}"
                )


api = AlbertAPI()

st.title("💬 Chatbot avec Albert")
st.subheader("Pose une question à Albert et il répondra avec humour.")
st.markdown(f"**url**: {api.base_url}")
st.markdown(
    "Avant de commencer, choisissez le mode de fonctionnement :"
    "\n\n* **normal** = tchat avec de l'humour"
    "\n* **RAG**: recherche de réponses dans le code source d'Albert (plus lent, garde aussi l'historique)"
    "\n\nPour changer de fonctionnement, il est préférable de vider le cache."
)
mode = st.radio("Choisissez le mode :", options=["Normal", "RAG"])

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "Tu es Albert, un chatbot intelligent et tu réponds toujours avec une plaisanterie.",
        }
    ]

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

user_input = st.chat_input("Pose ta question...")

if user_input:
    try:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        if mode == "Normal":
            reply = api.send_question(st.session_state.messages)
        elif mode == "RAG":
            reply = api.send_rag(st.session_state.messages)

        with st.chat_message("assistant"):
            st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

    except Exception as e:
        st.error(f"Erreur lors de l'appel à l'API Albert : {e}")
