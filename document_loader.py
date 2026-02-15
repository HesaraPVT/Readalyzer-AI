import os
import shutil # For safe directory removal
import pymupdf  # PyMuPDF
import docx
import requests

# ---- OLLAMA Setup ----
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# ---- LangChain imports ----
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

# ---- CONFIG ----
# Database path for Chroma
DB_PATH = "chroma_db"
UPLOAD_FOLDER = "uploaded_files"

# Make sure necessary folders exist
os.makedirs(DB_PATH, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load Ollama LLM
llm = OllamaLLM(model="mistral")

# Load Embedding model
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)

# ---- DOCUMENT EXTRACTION ----

def extract_text_from_pdf(path):
    text = ""
    try:
        doc = pymupdf.open(path)
        for page in doc:
            text += page.get_text("text") + "\n"
    except Exception as e:
        print(f"PDF Error: {e}")
    return text


def extract_text_from_word(path):
    text = ""
    try:
        doc = docx.Document(path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"DOCX Error: {e}")
    return text


def extract_text_from_txt(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"TXT Error: {e}")
        return ""


def extract_text(file_path):
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_word(file_path)
    elif file_path.endswith(".txt"):
        return extract_text_from_txt(file_path)
    else:
        print("Unsupported file:", file_path)
        return ""


# ---- DOCUMENT PROCESSING ----

def process_document(file_path):
    print(f"\nProcessing: {file_path}")

    if not os.path.exists(file_path):
        print("File not found!")
        return None

    text = extract_text(file_path)

    if not text.strip():
        print("No text extracted!")
        return None

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)

    print(f"Created {len(chunks)} chunks")
    return chunks


# ---- CHROMA DB FUNCTIONS ----

def safe_remove_db(db_path=DB_PATH):
    """Safely remove database with retry logic for Windows file locking"""
    import time
    import glob
    
    if not os.path.exists(db_path):
        return True
    
    # Try removing individual files first (SQLite is more cooperative)
    try:
        # Remove SQLite database files
        for db_file in glob.glob(os.path.join(db_path, "*.sqlite3")):
            try:
                os.remove(db_file)
            except Exception as e:
                print(f"Could not remove {os.path.basename(db_file)} (may still be locked)")
        
        # Remove other files recursively
        for root, dirs, files in os.walk(db_path, topdown=False):
            for file in files:
                try:
                    os.remove(os.path.join(root, file))
                except Exception:
                    pass  # Silently skip locked files
            for dir in dirs:
                try:
                    os.rmdir(os.path.join(root, dir))
                except Exception:
                    pass  # Silently skip if dir not empty or locked
    except Exception as e:
        print(f"Note: Some database files may still be in use, but will be overwritten")
    
    # Try removing the directory with retries
    max_retries = 2
    for attempt in range(max_retries):
        try:
            if os.path.exists(db_path):
                shutil.rmtree(db_path, ignore_errors=True)
            # Even if removal fails, just continue - Chroma will create fresh collections
            break
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(0.3)
    
    return True

def store_embeddings(chunks, db_path=DB_PATH):
    """Clear old DB and store new embeddings"""
    print("Clearing old database...")
    safe_remove_db(db_path)
    
    # Ensure directory exists
    os.makedirs(db_path, exist_ok=True)

    print("Storing new embeddings...")
    try:
        vectorstore = Chroma(
            collection_name="documents",
            embedding_function=embedding_model,
            persist_directory=db_path
        )
        vectorstore.add_texts(chunks)

        try:
            vectorstore.persist()
        except AttributeError:
            pass  # Auto-persist in newer versions
        print(f"Stored {len(chunks)} chunks")
    except Exception as e:
        print(f"Error storing embeddings: {e}")
        raise


def format_docs(docs):
    """Convert retrieved docs into clean text"""
    return "\n\n".join(doc.page_content for doc in docs)



# ---- RETRIEVAL + GENERATION ----

def build_retrieval_chain(db_path=DB_PATH):
    vectorstore = Chroma(
        collection_name="documents",
        embedding_function=embedding_model,
        persist_directory=db_path
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    prompt = ChatPromptTemplate.from_template("""
Use ONLY the context below to answer the question.

Context:
{context}

Question:
{question}
""")

    chain = (
        RunnableParallel({
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        })
        | prompt
        | llm
    )
    return chain


def search_and_summarize(query, db_path=DB_PATH):
    print(f"\nSearching: {query}")
    chain = build_retrieval_chain(db_path)
    try:
        response = chain.invoke(query)
        print("\nAI Response:")
        print(response)
        return response
    except Exception as e:
        print(f"Error during retrieval: {e}")
        return None


# ---- FASTAPI HELPER ----

def ingest_document(file_path):
    """Process + store embeddings for FastAPI uploads"""
    chunks = process_document(file_path)
    if chunks:
        store_embeddings(chunks)
        return True
    return False


# ---- OPTIONAL: MANUAL OLLAMA CALL ----

def generate_ai_response(context, question):
    prompt = f"""
Context:
{context}

Question:
{question}
"""
    payload = {"model": "mistral", "prompt": prompt, "stream": False}
    r = requests.post(OLLAMA_API_URL, json=payload)
    return r.json().get("response", "No response.")


# ---- TESTING ----

if __name__ == "__main__":
    sample_file = os.path.join(UPLOAD_FOLDER, "sample.pdf")

    success = ingest_document(sample_file)

    if success:
        while True:
            q = input("\nAsk a question (or 'exit'): ")
            if q.lower() == "exit":
                break
            search_and_summarize(q)
