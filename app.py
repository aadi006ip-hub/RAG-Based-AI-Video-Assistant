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
    source_input = st.text_input(
        "Media Source (URL or File Path)",
        value="https://www.youtube.com/watch?v=Q-e_nczWqM",
    )
    language_choice = st.selectbox(
        "Select Language / Model", options=["english", "hinglish"], index=0
    )
    st.markdown("---")
    process_btn = st.button(
        "🚀 Process Video", type="primary", use_container_width=True
    )

if process_btn:
    if not source_input.strip():
        st.error("Please provide a valid YouTube URL or media path.")
    else:
        try:
            with st.status(
                "Processing media pipeline...", expanded=True
            ) as status:
                transcript = None

                # STEP A: Direct fast transcript (Bypasses heavy download)
                if source_input.startswith(
                    "http://"
                ) or source_input.startswith("https://"):
                    st.write("⚡ Fetching direct transcript...")
                    transcript = try_get_youtube_transcript(source_input)

                # STEP B: Fallback to audio download if no direct transcript
                if not transcript:
                    st.write("📥 Processing audio...")
                    chunks = process_input(source_input)
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
    st.info("👈 Enter media link and click Process Video.")
