# RAG-based-document-Q-A-chatbot

A full-stack AI-powered chatbot that lets you upload any PDF document and ask questions about it in natural language. Built with FastAPI, LangChain, FAISS, HuggingFace Embeddings, and Google Gemini.

## How It Works

1. Upload a PDF document
2. The document gets split into chunks and indexed using HuggingFace embeddings stored in a FAISS vector store
3. When you ask a question, the system retrieves the most relevant chunks semantically
4. Google Gemini generates a precise answer based only on the retrieved context

## Tech Stack

**Backend**
- Python
- FastAPI — REST API framework
- LangChain — RAG orchestration
- FAISS — vector similarity search
- HuggingFace Sentence Transformers — local embeddings
- Google Gemini — LLM for answer generation

**Frontend**
- React
- Vite
- Tailwind CSS

## Project Structure
