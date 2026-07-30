from fastapi import FastAPI

app = FastAPI(
    title = "LifeStream API",
    version = "0.1.0",
    description="LifeStream的后端API"
)

@app.get("/health")
async def health_check() -> [str,str]:
    return {"status": "ok"}

