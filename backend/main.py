from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag import load_and_index_document, get_answer
from dotenv import load_dotenv
import shutil
import os

load_dotenv()

app = FastAPI()

vector_store = None
upload_status = {"status": "idle", "message": ""}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

def process_document(file_path: str):
    global vector_store, upload_status
    
    try:
        upload_status = {"status": "processing", "message": "Indexing document..."}
        vector_store = load_and_index_document(file_path)
        upload_status = {"status": "ready", "message": "Document ready. You can now ask questions."}
    
    except Exception as e:
        upload_status = {"status": "error", "message": f"Failed to process document: {str(e)}"}
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.get("/")
def root():
    return {"status": "RAG Chatbot API is running"}

@app.get("/status")
def get_status():
    return upload_status

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    global upload_status
    
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    file_path = f"temp_{file.filename}"
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        upload_status = {"status": "processing", "message": "Uploading document..."}
        background_tasks.add_task(process_document, file_path)
        
        return {"message": "File uploaded. Processing in background. Check /status for updates."}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file: {str(e)}"
        )

@app.post("/chat")
async def chat(request: QueryRequest):
    global vector_store, upload_status
    
    if upload_status["status"] == "processing":
        raise HTTPException(
            status_code=400,
            detail="Document is still being processed. Please wait."
        )
    
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