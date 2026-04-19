from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag import load_and_index_document, get_answer
from dotenv import load_dotenv
import shutil
import os

load_dotenv()

app = FastAPI()

vector_store = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

@app.get("/")
def root():
    return {"status": "RAG Chatbot API is running"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global vector_store
    
    file_path = f"temp_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    vector_store = load_and_index_document(file_path)
    os.remove(file_path)
    
    return {"message": f"{file.filename} uploaded and indexed successfully"}

@app.post("/chat")
async def chat(request: QueryRequest):
    global vector_store
    
    if vector_store is None:
        return {"error": "No document uploaded yet. Please upload a PDF first."}
    
    answer = get_answer(vector_store, request.question)
    return {"answer": answer}