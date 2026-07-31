import os
from dotenv import load_dotenv

load_dotenv()

import streamlit as st
from core.extractor import (
    extract_action_items,
    extract_key_decisions,
    extract_questions,
)
from core.summarizer import generate_title, summarize
from core.transcriber import transcribe_all, try_get_youtube_transcript
from utils.audio_processor import process_input

try:
    from core.rag_engine import query_rag
    from core.vector_store import build_vector_store

    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

st.set_page_config(
    page_title="RAG AI Video Assistant", page_icon="🎥", layout="wide"
)
st.title("🎥 RAG-Based AI Video Assistant")
st.caption("Extract summaries, transcripts, key insights, and chat using RAG.")
st.divider()

if "processed" not in st.session_state:
    st.session_state.processed = False
if "title" not in st.session_state:
    st.session_state.title = ""
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "action_items" not in st.session_state:
    st.session_state.action_items = ""
if "decisions" not in st.session_state:
    st.session_state.decisions = ""
if "questions" not in st.session_state:
    st.session_state.questions = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.sidebar:
    st.header("⚙️ Settings & Input")

    input_type = st.radio("Select Input Type:", ["YouTube URL", "Upload File"])

    source_input = None
    uploaded_file = None

    if input_type == "YouTube URL":
        source_input = st.text_input(
            "YouTube Video Link",
            value="https://www.youtube.com/watch?v=Q-e_nczWqM",
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload Audio/Video", type=["mp3", "wav", "mp4", "m4a"]
        )

    language_choice = st.selectbox(
        "Select Language / Model", options=["english", "hinglish"], index=0
    )
    st.markdown("---")
    process_btn = st.button(
        "🚀 Process Media", type="primary", use_container_width=True
    )

if process_btn:
    valid_input = False
    file_path = None

    if input_type == "YouTube URL" and source_input and source_input.strip():
        valid_input = True
        file_path = source_input.strip()
    elif input_type == "Upload File" and uploaded_file is not None:
        valid_input = True
        os.makedirs("downloades", exist_ok=True)
        file_path = os.path.join("downloades", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

    if not valid_input:
        st.error("Please provide a valid YouTube URL or upload a file.")
    else:
        try:
            with st.status(
                "Processing media pipeline...", expanded=True
            ) as status:
                transcript = None

                # Step 1: YouTube Fast Transcript Check
                if input_type == "YouTube URL":
                    st.write("⚡ Fetching direct transcript...")
                    transcript = try_get_youtube_transcript(file_path)

                # Step 2: Fallback / File Processing
                if not transcript:
                    st.write("📥 Processing audio chunks...")
                    chunks = process_input(file_path)
                    st.write("🎙️ Transcribing audio...")
                    transcript = transcribe_all(
                        chunks, language=language_choice
                    )
                else:
                    st.write("✅ Direct transcript fetched!")

                st.write("📌 Generating summary...")
                title = generate_title(transcript)
                summary = summarize(transcript)

                st.write("📊 Extracting insights...")
                action_items = extract_action_items(transcript)
                decisions = extract_key_decisions(transcript)
                questions = extract_questions(transcript)

                if RAG_AVAILABLE:
                    st.write("🧠 Building RAG Store...")
                    try:
                        build_vector_store(transcript)
                    except Exception as rag_err:
                        st.warning(f"RAG Notice: {rag_err}")

                st.session_state.title = title
                st.session_state.summary = summary
                st.session_state.transcript = transcript
                st.session_state.action_items = action_items
                st.session_state.decisions = decisions
                st.session_state.questions = questions
                st.session_state.chat_history = []
                st.session_state.processed = True

                status.update(
                    label="🎉 Processing Completed Successfully!",
                    state="complete",
                    expanded=False,
                )

        except Exception as e:
            st.error(f"Execution Error: {str(e)}")

if st.session_state.processed:
    st.subheader(f"📌 {st.session_state.title}")
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📝 Summary", "📊 Key Insights", "📄 Full Transcript", "💬 RAG Chat"]
    )

    with tab1:
        st.markdown("### Executive Summary")
        st.info(st.session_state.summary)

    with tab2:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 📋 Action Items")
            st.write(st.session_state.action_items)
        with col2:
            st.markdown("### 🔑 Key Decisions")
            st.write(st.session_state.decisions)
        with col3:
            st.markdown("### ❓ Open Questions")
            st.write(st.session_state.questions)

    with tab3:
        st.markdown("### Transcript")
        st.text_area(
            "Full transcript", st.session_state.transcript, height=350
        )
        st.download_button(
            "💾 Download (.txt)",
            st.session_state.transcript,
            file_name="transcript.txt",
        )

    with tab4:
        st.markdown("### 💬 Chat with Content")
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask a question..."):
            st.session_state.chat_history.append(
                {"role": "user", "content": prompt}
            )
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                if RAG_AVAILABLE:
                    try:
                        response = query_rag(prompt)
                    except Exception as err:
                        response = f"RAG Error: {err}"
                else:
                    response = "RAG Module optional."
                st.markdown(response)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": response}
                )
else:
    st.info("👈 Enter media link or upload file and click Process Media.")
