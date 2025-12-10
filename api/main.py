import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from api.routes import data, health, stats, admin
from prometheus_fastapi_instrumentator import Instrumentator
from core.logging_config import configure_logging
import logging

# Configure Structured Logging
configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Kasparro Backend Assignment", version="1.0.0")

# Instrument Prometheus Metrics
Instrumentator().instrument(app).expose(app)

@app.middleware("http")
async def add_process_time_and_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    request.state.start_time = time.time()
    
    response = await call_next(request)
    
    process_time = (time.time() - request.state.start_time) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(data.router)
app.include_router(stats.router)
app.include_router(admin.router, prefix="/admin", tags=["Admin"])

@app.get("/")
def root():
    return {"message": "Kasparro API is running. Check /docs for Swagger UI."}
