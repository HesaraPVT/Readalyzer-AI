# Readalyzer-AI
Readalyzer is a local RAG (Retrieval-Augmented Generation) application that allows you to "talk" to your documents. It uses FastAPI for a robust backend, Streamlit for a sleek user interface, and Ollama to run the Mistral LLM entirely on your local machine ensuring your data stays private.

# **Features**
* Multi-Format Support: Upload and index .pdf, .docx, and .txt files.
* Local Processing: Powered by Mistral via Ollama and Sentence-Transformers for privacy-focused      embeddings.
* Vector Search: Uses ChromaDB to find relevant context before answering.
* Interactive UI: A clean, modern chat interface built with Streamlit.

# **Requirements**
Before you start, ensure you have the following installed:
1. Python 3.10+
2. Ollama: [https://ollama.com](https://ollama.com/)
3. Mistral Model: Once Ollama is installed, run
   ```ollama pull mistral``` in CMD.

# **Installation & Setup**
1.Clone the Repository
```git clone https://github.com/your-username/readalyzer.git```
```cd readalyzer```
