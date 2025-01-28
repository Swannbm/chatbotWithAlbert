import logging
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


logger = logging.getLogger(f"uvicorn.{__name__}")

load_dotenv(dotenv_path=Path(__file__).parent / ".env")


app = FastAPI()


class AlbertAPI:
    """Call AlbertAPI endpoints.

    ..TODO: factorize with same class in streamlit_chat.py
    """

    def __init__(self):
        self.api_key = os.getenv("ALBERT_API_KEY")
        self.base_url = (
            f"{os.getenv('ALBERT_API_ROOT')}/{os.getenv('ALBERT_API_VERSION')}"
        )
        self.model = "mistralai/Pixtral-12B-2409"

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def get_endpoint_url(self, endpoint):
        return f"{self.base_url}/{endpoint}"

    def send_question(self, messages):
        """Sen messages to AlbertAPI chat endpoint then return the answer."""
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


albert_api = AlbertAPI()


# Serializers


class ChatSerializer(BaseModel):
    messages: list


# FastAPI routes


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API pour interroger AlbertAPI !"}


# no end slash for compatibility with streamlit_chat.py and AlberAPI
@app.post("/chat/completions")
def chat_with_albert(request: ChatSerializer):
    try:
        logger.info(request)
        reply = albert_api.send_question(request.messages)
        return {"reply": reply}
    except Exception as e:
        # Gestion des erreurs HTTP
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de l'appel à l'API Albert : {str(e)}"
        ) from e
