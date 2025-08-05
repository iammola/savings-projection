import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

from extract import extract

load_dotenv()
app = FastAPI()


class ExtractText(BaseModel):
    text: str


@app.post("/extract")
def extract_entities(text: ExtractText):
    return extract(text.text)


def start_server():
    uvicorn.run(app, port=int(os.environ.get("API_PORT")))


if __name__ == "__main__":
    start_server()
