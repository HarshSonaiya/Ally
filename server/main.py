from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.routes import router

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow requests from your frontend URL (Vite dev server)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include the PDF processing routes from the controller
app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Navio!!!"}