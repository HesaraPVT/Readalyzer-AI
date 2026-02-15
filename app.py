from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import os
import shutil
import gc

# Import your document loader functions
from document_loader import ingest_document, DB_PATH, embedding_model, llm
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough


# ---- FastAPI App ----

app = FastAPI(title="Mistral AI-powered Search API")

# Ensure upload folder exists
UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---- Helper to reload Chroma DB ----

def reload_vectorstore():
    vectorstore = Chroma(
        collection_name="documents",
        persist_directory=DB_PATH,
        embedding_function=embedding_model
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    return vectorstore, retriever

# Load initial vectorstore (or set to None if DB doesn't exist yet)
try:
    vectorstore, retriever = reload_vectorstore()
except Exception as e:
    print(f"Could not load initial vectorstore: {e}")
    vectorstore, retriever = None, None

# Prompt template for QA
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="Context: {context}\n\nQuestion: {question}\n\nAnswer:"
)

# Build retrieval chain
def build_qa_chain():
    return (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt_template
        | llm
    )

qa_chain = build_qa_chain()

# ---- Request schema ----

class QueryRequest(BaseModel):
    query: str


# ---- Endpoints ----

@app.get("/")
async def home():
    return {"message": "Mistral AI-powered search API is running!"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    global vectorstore, retriever, qa_chain
    
    try:
        # Save the uploaded file
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        # Clear old vectorstore to release database lock
        vectorstore = None
        retriever = None
        qa_chain = None
        
        # Force garbage collection to release file handles
        gc.collect()
        
        # Ingest document (clears old DB and stores new embeddings)
        success = ingest_document(file_path)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to process document")

        # Reload vectorstore and chain
        vectorstore, retriever = reload_vectorstore()
        qa_chain = build_qa_chain()

        return {"message": f"Document '{file.filename}' uploaded and indexed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/query")
async def search_and_generate_response(request: QueryRequest):
    try:
        response = qa_chain.invoke(request.query)
        return {"query": request.query, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
