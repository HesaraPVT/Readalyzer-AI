# Readalyzer-AI
Readalyzer is a local RAG (Retrieval-Augmented Generation) application that allows you to "talk" to your documents. It uses FastAPI for a robust backend, Streamlit for a sleek user interface, and Ollama to run the Mistral LLM entirely on your local machine ensuring your data stays private.

![image alt](https://github.com/HesaraPVT/Readalyzer-AI/blob/49a70fd1c9d83981ec688a5107bd233a6f410fa0/Readalyzer.png)

# **Features**
* Multi-Format Support: Upload and index .pdf, .docx, and .txt files.
* Local Processing: Powered by Mistral via Ollama and Sentence-Transformers for privacy-focused      embeddings.
* Vector Search: Uses ChromaDB to find relevant context before answering.
* Interactive UI: A clean, modern chat interface built with Streamlit.

# **Requirements**
Before you start, ensure you have the following installed:
* Python 3.10+
*  Ollama: [https://ollama.com](https://ollama.com/)
*  Mistral Model: Once Ollama is installed, run
   ```ollama pull mistral``` in CMD.

# **Installation & Setup**
* Clone the Repository
```git clone https://github.com/your-username/readalyzer.git``` then run
```cd readalyzer```
* Create a Virtual Environment (venv)
Windows
```python -m venv venv```
```venv\Scripts\activate```

macOS/Linux
```python3 -m venv venv```
```source venv/bin/activate```
* Install Dependencies
Create a requirements.txt file in your root folder with the following content:

fastapi
uvicorn
streamlit
langchain
langchain-community
langchain-chroma
langchain-ollama
langchain-core
sentence-transformers
pymupdf
python-docx
requests
pydantic

Then run: ```pip install -r requirements.txt```

# **How to Run**
You need to run the Backend and the Frontend in two separate terminals.Before that you need to deactivate conda from both terminals using ```conda deactivate``` then run ```venv\Scripts\activate``` just to make sure both terminals are in virtual environment.
* Step 1: Start the FastAPI Backend
```uvicorn app:app --reload```
The backend will be running at http://127.0.0.1:8000.

* Step 2: Start the Streamlit UI
```streamlit run app_ui.py```
The UI will open automatically in your browser (usually at http://localhost:8501).

# **Usage Guide**
* Upload: Use the sidebar in the Streamlit app to upload a PDF, Word, or Text file.
* Wait: The backend will extract the text, split it into chunks, and store embeddings in the     chroma_db folder.
* Chat: Type your question in the text box and hit "Ask AI". The bot will only answer based      on the document you provided.

# **Project Structure**
* ```document_loader.py```: The "brain"—handles text extraction, chunking, and vector database   logic.
* ```app.py```: The FastAPI server that handles file uploads and query routing.
* ```app_ui.py```: The Streamlit frontend for the user.
* ```uploaded_files/```: Temporary storage for your uploaded documents.
* ```chroma_db/```: Persistent storage for the vector embeddings.
* ```venv/```: Self-contained directory that contains the Python installation for this project.
* ```__pycache__/```: A folder automatically created by Python when you run your code. It        contains "bytecode" (.pyc files).
* ```static/```: A folder used to store fixed assets that don't change while the app is          running.

# **Important Note on Database Locking**
This project includes "safe removal" logic for ChromaDB. If you encounter file-access errors on Windows when uploading a new document, the app will automatically attempt to clear the locks and refresh the collection.

# **Contributing**
Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.
* Fork the Project
* Create your Feature Branch (git checkout -b feature/AmazingFeature)
* Commit your Changes (git commit -m 'Add some AmazingFeature')
* Push to the Branch (git push origin feature/AmazingFeature)
* Open a Pull Request

```If this project helped you, please give it a ⭐ to show your support!!!```
