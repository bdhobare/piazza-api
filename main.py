from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Hello from Piazza API"}


@app.get("/health")
def health():
    return {"status": "ok"}