from fastapi import FastAPI

from app.api.v1.routes import shopping, room

app = FastAPI(title= "Shopping List API")

# Register routes
app.include_router(shopping.router)
app.include_router(room.router)
