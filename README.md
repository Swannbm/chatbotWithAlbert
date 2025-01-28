# chatbotWithAlbert

It contains two app.
1/ a simple ChatBot built with Streamlit
2/ a FastAPI server that handle auth to contact AlbertAPI

## Chat bot

A simple ChatBot with Streamlit and Albert API.

How to install and use it:

* Copy / past .env.example in .env and complete each variable.
* Install poetry then run `poetry install`
* Enter poetry shell `poetry shell`
* Launch the chat bot `make chat`

 You can use it without the FastAPI server, to do so, fill .env APIROOT with the url of AlbertAPI staging.

## FastAPI server

Install and start:

* It also requires to complete the .env file.
* type: `make startfast`
