"""SAP AI Assistant — Streamlit Demo UI"""
from __future__ import annotations

import base64
import json

import httpx
import streamlit as st
import streamlit.components.v1 as components

# ── Config ──
API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="SAP AI Assistant",
    page_icon="🤖",
    layout="wide",
)

# ── Styles ──
st.markdown("""
<style>
    .source-card {
        background: #f0f2f6;
        border-radius: 8px;
        padding: 12px;
        margin: 4px 0;
        border-left: 3px solid #1f77b4;
    }
    .score-badge {
        background: #1f77b4;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8em;
    }
    .main-header {
        text-align: center;
        padding: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def _copy_button(text: str, key: str = "copy") -> None:
    """Render a small copy-to-clipboard button via JS."""
    b64 = base64.b64encode(text.encode()).decode()
    copied_label = "&#x2705; Copied!"
    default_label = "&#x1F4CB; Copy"
    components.html(
        f"""
        <script>
        function fallbackCopy_{key}(text) {{
            var ta = document.createElement('textarea');
            ta.value = text;
            ta.style.position = 'fixed';
            ta.style.left = '-9999px';
            document.body.appendChild(ta);
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
            document.getElementById('btn_{key}').innerHTML = '{copied_label}';
            setTimeout(function() {{ document.getElementById('btn_{key}').innerHTML = '{default_label}'; }}, 2000);
        }}
        function doCopy_{key}() {{
            var text = atob('{b64}');
            if (navigator.clipboard && navigator.clipboard.writeText) {{
                navigator.clipboard.writeText(text).then(function() {{
                    document.getElementById('btn_{key}').innerHTML = '{copied_label}';
                    setTimeout(function() {{ document.getElementById('btn_{key}').innerHTML = '{default_label}'; }}, 2000);
                }}).catch(function() {{ fallbackCopy_{key}(text); }});
            }} else {{
                fallbackCopy_{key}(text);
            }}
        }}
        </script>
        <button id="btn_{key}" onclick="doCopy_{key}()"
            style="background:transparent; color:#888; border:1px solid #555;
                   padding:3px 10px; border-radius:6px; cursor:pointer;
                   font-size:0.85em;">
            {default_label}
        </button>
        """,
        height=38,
    )

# ── Header ──
st.markdown("<h1 class='main-header'>🤖 SAP AI Assistant</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:#666'>Ask questions about SAP S/4HANA, SuccessFactors, "
    "Hyland integrations, and more</p>",
    unsafe_allow_html=True,
)

# ── Sidebar ──
with st.sidebar:
    st.header("⚙️ Settings")

    module_filter = st.selectbox(
        "SAP Module Filter",
        ["All Modules", "S4HANA", "SuccessFactors", "OnBase", "CIC", "Alfresco"],
    )
    if module_filter == "All Modules":
        module_filter = None

    st.divider()

    st.header("📄 Upload Documents")
    uploaded_file = st.file_uploader(
        "Upload SAP documentation",
        type=["pdf", "html", "md", "txt", "docx"],
    )
    upload_module = st.text_input("Tag with SAP Module (optional)")

    if uploaded_file and st.button("📥 Ingest Document"):
        with st.spinner("Ingesting document..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                params = {"module": upload_module} if upload_module else {}
                response = httpx.post(
                    f"{API_BASE}/documents/upload",
                    files=files,
                    params=params,
                    timeout=120,
                )
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ Ingested! {result['chunks_created']} chunks created.")
                else:
                    st.error(f"❌ Error: {response.text}")
            except httpx.ConnectError:
                st.error("❌ Cannot connect to API. Is the backend running?")

    st.divider()

    st.header("🔗 Ingest from URL")
    url_input = st.text_area(
        "Paste public URLs (one per line)",
        placeholder="https://help.sap.com/docs/...\nhttps://community.sap.com/...",
        height=100,
    )
    url_module = st.text_input("Tag URLs with SAP Module (optional)", key="url_module")

    if url_input and st.button("🌐 Ingest URLs"):
        urls = [u.strip() for u in url_input.strip().splitlines() if u.strip()]
        if urls:
            with st.spinner(f"Ingesting {len(urls)} URL(s)..."):
                try:
                    response = httpx.post(
                        f"{API_BASE}/documents/url",
                        json={"urls": urls, "module": url_module},
                        timeout=120,
                    )
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ Ingested {result['urls_processed']} URL(s)! {result['chunks_created']} chunks created.")
                    else:
                        st.error(f"❌ Error: {response.text}")
                except httpx.ConnectError:
                    st.error("❌ Cannot connect to API. Is the backend running?")

    st.divider()

    # Stats
    st.header("📊 Knowledge Base")
    try:
        health = httpx.get(f"{API_BASE}/health", timeout=5).json()
        st.metric("Documents Indexed", health["document_count"])
        st.metric("Vector Store", health["vector_store"])
        st.metric("Status", health["status"])
    except Exception:
        st.warning("Backend not connected")

    if st.button("🗑️ Reset Knowledge Base", type="secondary"):
        try:
            response = httpx.delete(f"{API_BASE}/documents/reset", timeout=30)
            if response.status_code == 200:
                result = response.json()
                st.success(f"✅ Reset! {result['chunks_deleted']} chunks deleted.")
                st.rerun()
            else:
                st.error(f"❌ Error: {response.text}")
        except httpx.ConnectError:
            st.error("❌ Cannot connect to API.")


# ── Chat Interface ──
if "messages" not in st.session_state:
    st.session_state.messages = []


def _render_sources(sources: list, key_prefix: str) -> None:
    """Render source cards inside an expander."""
    if not sources:
        return
    with st.expander("📚 Sources"):
        for src in sources:
            page_str = f" (Page {src['page']})" if src.get('page') else ""
            st.markdown(
                f"<div class='source-card'>"
                f"<strong>[Source {src['index']}]</strong> {src['source']}"
                f"{page_str}"
                f" <span class='score-badge'>{src['score']:.0%}</span>"
                f"<br><small>{src['preview']}</small>"
                f"</div>",
                unsafe_allow_html=True,
            )


def _send_question(question: str) -> None:
    """Send a question to the API and store the result in session state."""
    try:
        response = httpx.post(
            f"{API_BASE}/chat",
            json={
                "question": question,
                "module_filter": module_filter,
                "stream": False,
            },
            timeout=120,
        )

        if response.status_code == 200:
            data = response.json()
            st.session_state.messages.append({
                "role": "assistant",
                "content": data["answer"],
                "sources": data.get("sources", []),
            })
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ Server error ({response.status_code}): {response.text[:300]}",
                "error": True,
                "failed_question": question,
            })
    except httpx.ConnectError:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "❌ Cannot connect to the API backend. Make sure the server is running.",
            "error": True,
            "failed_question": question,
        })
    except Exception as exc:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"❌ Unexpected error: {exc}",
            "error": True,
            "failed_question": question,
        })


# Handle pending retry (set before a rerun)
if st.session_state.get("_retry_question"):
    q = st.session_state.pop("_retry_question")
    st.session_state.messages.append({"role": "user", "content": q})
    _send_question(q)

# Display chat history
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        if msg.get("error"):
            st.error(msg["content"])
            if st.button("🔄 Retry", key=f"retry_{i}"):
                failed_q = msg["failed_question"]
                # Remove the error message and the user question before it
                st.session_state.messages = [
                    m for j, m in enumerate(st.session_state.messages)
                    if j != i and j != i - 1
                ]
                st.session_state["_retry_question"] = failed_q
                st.rerun()
        else:
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                _copy_button(msg["content"], key=f"copy_{i}")
                _render_sources(msg.get("sources", []), key_prefix=f"src_{i}")

# Chat input
if prompt := st.chat_input("Ask about SAP..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base and generating answer..."):
            _send_question(prompt)

        # Display the just-added assistant message
        last = st.session_state.messages[-1]
        if last.get("error"):
            st.error(last["content"])
            # Retry will be available on next rerun via the history loop
        else:
            st.markdown(last["content"])
            _copy_button(last["content"], key="copy_latest")
            _render_sources(last.get("sources", []), key_prefix="src_latest")
