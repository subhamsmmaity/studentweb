from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from database import init_db
from routers import auth, academics, productivity, community, career

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="change-this-secret-key-later")
app.mount("/static", StaticFiles(directory="static"), name="static")

init_db()

app.include_router(auth.router)
app.include_router(academics.router)
app.include_router(productivity.router)
app.include_router(community.router)
app.include_router(career.router)