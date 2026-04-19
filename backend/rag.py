from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv
import os

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Check your .env file.")

def load_and_index_document(file_path: str):
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        if not documents:
            raise ValueError("No text could be extracted from the PDF. The file may be empty or scanned.")
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        chunks = splitter.split_documents(documents)
        
        if not chunks:
            raise ValueError("Document could not be split into chunks. It may be too short.")
        
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vector_store = FAISS.from_documents(chunks, embeddings)
        
        return vector_store
    
    except ValueError as e:
        raise e
    
    except Exception as e:
        raise Exception(f"Failed to load and index document: {str(e)}")

def get_answer(vector_store, question: str):
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=gemini_api_key
        )
        
        retriever = vector_store.as_retriever(
            search_kwargs={"k": 3}
        )

        prompt = PromptTemplate.from_template("""
        Answer the question based only on the context below.
        If the answer is not in the context, say "I could not find the answer in the document."
        
        Context: {context}
        
        Question: {question}
        """)

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        return chain.invoke(question)
    
    except Exception as e:
        raise Exception(f"Failed to generate answer: {str(e)}")