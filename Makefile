include .env
export $(shell sed 's/=.*//' .env)


lint:
	ruff check . --fix
	ruff format .

chat:
	streamlit run app.py
