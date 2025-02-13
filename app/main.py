from fastapi import FastAPI

from app.api.v1.routes import shopping, room, websockets

app = FastAPI(title= "Shopping List API")

# Register routes
app.include_router(shopping.router)
app.include_router(room.router)

# Register WebSocket route
app.include_router(websockets.router)
