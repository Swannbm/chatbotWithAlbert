import os

import requests
from dotenv import load_dotenv
import streamlit as st


load_dotenv()


class AlbertAPI:
    def __init__(self):
        self.api_key = os.getenv("APIKEY")
        self.base_url = f"{os.getenv('APIROOT')}/{os.getenv('APIVERSION')}"
        self.model = "mistralai/Pixtral-12B-2409"

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def get_endpoint_url(self, endpoint):
        return f"{self.base_url}/{endpoint}"

    def send_question(self, messages):
        data = {
            "model": self.model,
            "messages": messages,
        }
        response = requests.post(
            self.get_endpoint_url("chat/completions"),
            headers=self.get_headers(),
            json=data,
        )
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]


api = AlbertAPI()

st.title("💬 Chatbot avec Albert")
st.subheader("Pose une question à Albert et il répondra avec humour.")

st.markdown(f"**url**: {api.base_url}")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "Tu es Albert, un chatbot intelligent et tu réponds toujours avec une plaisanterie.",
        }
    ]

with st.form("chat_form"):
    user_input = st.text_input("Pose ta question :", "")
    submitted = st.form_submit_button("Envoyer")

    if submitted and user_input:
        try:
            st.session_state.messages.append({"role": "user", "content": user_input})
            reply = api.send_question(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            st.error(f"Erreur lors de l'appel à l'API Albert : {e}")

for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"**Vous :** {message['content']}")
    elif message["role"] == "assistant":
        st.markdown(f"**Albert :** {message['content']}")
