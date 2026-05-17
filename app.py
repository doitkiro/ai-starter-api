from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/logs")
def get_logs(queue:str):
    if queue == "payment.queue":
        return {
            "queue": queue,
            "backlog": 17,
            "status": "healthy",
            "message": "Queue operating normally"
        }
    return {
        "queue": queue,
        "backlog": 1717,
        "status": "warning",
        "message": "Queue backlog increasing repidly"
    }