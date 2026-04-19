from fastapi import FastAPI, UploadFile, File, HTTPException
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
    
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    file_path = f"temp_{file.filename}"
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        vector_store = load_and_index_document(file_path)
        
        return {"message": f"{file.filename} uploaded and indexed successfully"}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {str(e)}"
        )
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/chat")
async def chat(request: QueryRequest):
    global vector_store
    
    if vector_store is None:
        raise HTTPException(
            status_code=400,
            detail="No document uploaded yet. Please upload a PDF first."
        )
    
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )
    
    try:
        answer = get_answer(vector_store, request.question)
        return {"answer": answer}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate answer: {str(e)}"
        )