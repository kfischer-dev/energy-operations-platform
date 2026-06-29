from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Energy Operations Platform API"}

@app.get("/health")
def app_status():
    return {"Status": "ok"}