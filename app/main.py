from fastapi import FastAPI

from app.api.v1.routes import shopping

app = FastAPI(title= "Shopping List API")

# Register routes
app.include_router(shopping.router)
