import os
from dotenv import load_dotenv

# MUST be loaded before any core/ imports
load_dotenv()

import streamlit as st

# Standard imports matching test.py
from core.extractor import (
    extract_action_items,
    extract_key_decisions,
    extract_questions,
)
from core.summarizer import generate_title, summarize
from core.transcriber import transcribe_all
from utils.audio_processor import process_input

# Optional imports for RAG Q&A integration if available in core
try:
    from core.rag_engine import query_rag
    from core.vector_store import build_vector_store

    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False


# -----------------------------------------------------------------------------
# Page Configuration & Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="RAG AI Video Assistant",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🎥 RAG-Based AI Video Assistant")
st.caption(
    "Extract summaries, transcripts, key insights, and chat with your media"
    " using RAG."
)
st.divider()

# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# Sidebar Configuration
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings & Input")

    source_input = st.text_input(
        "Media Source (URL or File Path)",
        value="https://www.youtube.com/watch?v=Q-e_nczWqM&t=223s",
        help="Paste a YouTube link or local audio/video file path.",
    )

    language_choice = st.selectbox(
        "Select Language / Model",
        options=["english", "hinglish"],
        index=0,
        help="`english` uses Whisper, `hinglish` uses Sarvam AI.",
    )

    st.markdown("---")
    process_btn = st.button(
        "🚀 Process Video", type="primary", use_container_width=True
    )

# -----------------------------------------------------------------------------
# Core Processing Pipeline Execution
# -----------------------------------------------------------------------------
if process_btn:
    if not source_input.strip():
        st.error("Please provide a valid YouTube URL or media path.")
    else:
        try:
            with st.status(
                "Processing media pipeline...", expanded=True
            ) as status:
                st.write("📥 Step 1/5: Processing audio chunks...")
                chunks = process_input(source_input)

                st.write(
                    f"🎙️ Step 2/5: Transcribing using **{language_choice}**"
                    " model..."
                )
                # Updated to pass source_input for fast YouTube transcript fetch
                transcript = transcribe_all(
                    chunks, language=language_choice, source=source_input
                )

                st.write("📌 Step 3/5: Generating title and summary...")
                title = generate_title(transcript)
                summary = summarize(transcript)

                st.write("📊 Step 4/5: Extracting key insights...")
                action_items = extract_action_items(transcript)
                decisions = extract_key_decisions(transcript)
                questions = extract_questions(transcript)

                # Optional Vector Indexing for RAG
                if RAG_AVAILABLE:
                    st.write("🧠 Step 5/5: Building RAG Vector Store Index...")
                    try:
                        build_vector_store(transcript)
                    except Exception as rag_err:
                        st.warning(f"Vector Store building notice: {rag_err}")

                # Save results to session state
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

# -----------------------------------------------------------------------------
# Main Dashboard Layout
# -----------------------------------------------------------------------------
if st.session_state.processed:
    st.subheader(f"📌 {st.session_state.title}")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📝 Summary", "📊 Key Insights", "📄 Full Transcript", "💬 RAG Chat"]
    )

    # Tab 1: Title & Executive Summary
    with tab1:
        st.markdown("### Executive Summary")
        st.info(st.session_state.summary)

    # Tab 2: Categorized Insights
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

    # Tab 3: Full Transcript view with quick download
    with tab3:
        st.markdown("### Transcript")
        st.text_area(
            "Full extracted transcript",
            st.session_state.transcript,
            height=350,
        )
        st.download_button(
            label="💾 Download Transcript (.txt)",
            data=st.session_state.transcript,
            file_name="transcript.txt",
            mime="text/plain",
        )

    # Tab 4: Interactive RAG Chat Bot
    with tab4:
        st.markdown("### 💬 Chat with your Video Content")

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask a question about this video..."):
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
                        response = f"RAG Query failed: {err}"
                else:
                    response = (
                        "RAG module functions (`query_rag`) can be hooked up"
                        " directly in `core/rag_engine.py` to enable"
                        " interactive Q&A."
                    )

                st.markdown(response)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": response}
                )

else:
    st.info(
        "👈 Enter your media link or file path in the sidebar and click"
        " **Process Video** to get started."
    )
