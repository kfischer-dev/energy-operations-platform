import uvicorn


if __name__ == "__main__":
    print("Starting Energy Operations Platform API...")
    print("Server: http://127.0.0.1:8000")
    print("Docs:   http://127.0.0.1:8000/docs")
    print("Stop:   CTRL + C")

    uvicorn.run(
        "src.api:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=["src"],
        log_level="info",
    )