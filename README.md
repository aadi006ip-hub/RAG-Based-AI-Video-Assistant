# # RAG-Based AI Video Assistant
An intelligent, Retrieval-Augmented Generation (RAG) system designed to analyze, process, and query video content using Large Language Models (LLMs) and vector embeddings. Ask questions about your video content and receive accurate, context-aware answers grounded in video transcripts or visual context.

[![Streamlit App](streamlit.jpg)](https://rag-based-ai-video-assistant-vfbqkzajha7nlirzxkxd9w.streamlit.app/)

## 📌 Project Structure
```text
RAG-Based-AI-Video-Assistant/
├── core/               # Core business logic (RAG pipeline, embeddings, LLM chains)
├── utils/              # Helper functions (video processing, transcription, audio extraction)
├── app.py              # Web Interface (Streamlit / Gradio front-end)
├── main.py             # Entry point / CLI execution script
├── test.py             # Unit tests and system validation scripts
├── requirements.txt    # Project dependencies
└── .gitignore          # Git ignore configuration

```
## ✨ Features
 * **Video Processing & Transcription:** Automatically extracts audio/transcripts from uploaded video files or links.
 * **Vector Indexing & Retrieval:** Chunking and embedding video context into a vector database for semantic search.
 * **Contextual Q&A (RAG):** Leverages an LLM to answer detailed user queries with precise citations from the video.
 * **User-Friendly Interface:** Interactive web application for easy file uploading and chat interface (app.py).
## 🛠️ Tech Stack
 * **Language:** Python 3.9+
 * **LLM & RAG Framework:** LangChain / LlamaIndex
 * **Embeddings & Vector Store:** FAISS / ChromaDB / OpenAI Embeddings
 * **UI Framework:** Streamlit / Gradio
 * **Audio Processing:** OpenAI Whisper / PyPDF / moviepy
## 🚀 Getting Started
### 1. Prerequisites
Make sure you have Python 3.9 or higher installed on your machine.
### 2. Installation
Clone the repository and install the required dependencies:
```bash
# Clone the repository
git clone https://github.com/aadi006ip-hub/RAG-Based-AI-Video-Assistant.git

# Navigate to the project directory
cd RAG-Based-AI-Video-Assistant

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

```
### 3. Environment Setup
Create a .env file in the root directory and add your secret API keys:
```env
OPENAI_API_KEY=your_openai_api_key_here
# GROQ_API_KEY=your_groq_api_key_here (if applicable)

```
## 🎯 Usage
### Running the Web Application
Launch the interactive UI using Streamlit:
```bash
streamlit run app.py

```
### Running via CLI / Core Pipeline
To execute the pipeline directly via terminal:
```bash
python main.py

```
### Running Tests
To verify everything is working correctly, run the test suite:
```bash
python test.py

```
## 📄 License
This project is licensed under the MIT License.
