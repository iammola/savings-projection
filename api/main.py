from fastapi import FastAPI

import extract

app = FastAPI()

@app.post("/extract")
def extract_entities(text: str):
    return extract.extract(text)

def run():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
