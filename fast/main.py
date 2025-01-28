import logging
import os
from pathlib import Path
from typing import List

from openai import OpenAI
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


logger = logging.getLogger(f"uvicorn.{__name__}")

load_dotenv(dotenv_path=Path(__file__).parent / ".env")


app = FastAPI()


class AlbertAPI:
    """Call AlbertAPI endpoints."""

    def __init__(self):
        self.api_key = os.getenv("ALBERT_API_KEY")
        self.base_url = (
            f"{os.getenv('ALBERT_API_ROOT')}/{os.getenv('ALBERT_API_VERSION')}"
        )

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def get_endpoint_url(self, endpoint):
        return f"{self.base_url}/{endpoint}"

    def send_question(self, messages: List, model: str = "mistralai/Pixtral-12B-2409"):
        """Send messages to AlbertAPI chat endpoint then return the answer."""
        data = {
            "model": model,
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

    def send_rag_prompt(self, collection_id: str, messages: List, method: str = "semantic"):
        """Send a prompt to AlbertAPI RAG endpoint then return the answer.

        collection_id: choose the collection to search in
        prompt: the question to ask
        method: the search method to use
        """
        prompt = messages[-1]["content"]
        data = {
            "collections": [collection_id],
            "k": 6,
            "prompt": prompt,
            "method": method,
        }
        response = requests.post(
            self.get_endpoint_url("search"),
            headers=self.get_headers(),
            json=data,
        )
        response.raise_for_status()
        chunks = "\n\n\n".join(
            [result["chunk"]["content"] for result in response.json()["data"]]
        )
        rag_prompt = f"Réponds à la question suivante en te basant sur les documents ci-dessous : {prompt}\n\nDocuments :\n\n{chunks}"
        # TODO : replace below by direct call to AlbertAPI
        client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        # replace last prompt by improved prompt using files
        messages[-1] = {"role": "user", "content": rag_prompt}
        logger.debug(messages)
        response = client.chat.completions.create(
            messages=messages,
            model="AgentPublic/llama3-instruct-8b",
            stream=False,
            n=1,
        )
        return response.choices[0].message.content


albert_api = AlbertAPI()


# Serializers


class ChatSerializer(BaseModel):
    messages: list


class RagPromptSerializer(BaseModel):
    prompt: str


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


@app.post("/rag/albert-source-code/")
def improve_albert_api(request: ChatSerializer):
    try:
        logger.info(request)
        reply = albert_api.send_rag_prompt(
            collection_id="86795f81-6ec0-4955-9e34-d04d1327f8a5", messages=request.messages
        )
        return {"reply": reply}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de l'appel à l'API Albert : {str(e)}"
        ) from e
