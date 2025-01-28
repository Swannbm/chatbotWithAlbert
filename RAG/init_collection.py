import io
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from fpdf import FPDF


load_dotenv(Path(__file__).parent / ".env")


# configuration

language_model = "AgentPublic/llama3-instruct-8b"
embeddings_model = "BAAI/bge-m3"
collection = "source-code-albert-api"
collection_id = "86795f81-6ec0-4955-9e34-d04d1327f8a5"
base_url = f"{os.getenv('ALBERT_API_ROOT')}/{os.getenv('ALBERT_API_VERSION')}"
api_key = os.getenv("ALBERT_API_KEY")


session = requests.session()
session.headers = {"Authorization": f"Bearer {os.getenv('ALBERT_API_KEY')}"}


response = session.get(f"{base_url}/documents/{collection_id}")
already_uploaded = [_["name"] for _ in response.json()["data"]]

print("Already uploaded:", already_uploaded)


def convert_py_to_pdf(input_file):
    # improvement: use pygment to highlight the code
    pdf = FPDF()
    pdf.add_font("DejaVu", "", "RAG/fonts/DejaVuSans.ttf")
    pdf.set_font("DejaVu", size=10)
    pdf.add_page()

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            pdf.multi_cell(0, 10, line)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)

    return buffer


source = Path("/home/swann/albert-api")
for file_path in source.rglob("*.py"):
    # keep directory name to avoid conflicts
    relative_path = file_path.relative_to(source)
    name = str(relative_path).replace("/", "_").replace(".py", ".pdf")
    if name in already_uploaded:
        # jump to next document
        continue

    try:
        content = convert_py_to_pdf(file_path)
        response = session.post(
            f"{base_url}/files",
            #"http://httpbin.org/post",
            data={"request": '{"collection": "%s"}' % collection_id},
            files={"file": (name, content, "application/pdf")},
        )
        response.raise_for_status()
    except Exception as e:
        print(f"Error with {file_path}: {e}")
