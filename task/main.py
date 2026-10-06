from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.task_router import task_router
from core.lifespan import lifespan

app = FastAPI(lifespan=lifespan, title="Task Project", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(task_router, prefix="/tasks")
