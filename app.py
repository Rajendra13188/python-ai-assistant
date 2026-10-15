
import re
import requests
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Python AI Assistant",
    page_icon="🐍",
    layout="wide"
)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:1b"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "prompt" not in st.session_state:
    st.session_state.prompt = ""

if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #050816, #0b1230 55%, #10102a);
    color: #e6edff;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080f27, #101633);
    border-right: 1px solid #26345e;
}
.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 7rem;
}
h1 {
    background: linear-gradient(90deg, #27d8f2, #7795ff, #c18cff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero {
    padding: 28px;
    border: 1px solid #354b91;
    border-radius: 22px;
    background: linear-gradient(120deg, #121e43, #211544);
    margin: 16px 0 26px 0;
    animation: fadeIn 0.6s ease;
}
.feature {
    padding: 20px;
    min-height: 135px;
    border-radius: 15px;
    background: linear-gradient(145deg, #12294a, #172344);
    border: 1px solid #263d69;
    transition: transform .2s ease, border-color .2s ease;
}
.feature:hover {
    transform: translateY(-4px);
    border-color: #5b8dff;
}
.status {
    background: #09232e;
    border: 1px solid #007f80;
    border-radius: 14px;
    padding: 16px;
    color: #5fffe0;
}
.stButton button, .stDownloadButton button {
    border-radius: 12px;
    border: 1px solid #3456a2;
    transition: all .2s ease;
}
.stButton button:hover, .stDownloadButton button:hover {
    border-color: #55dfff;
    transform: translateY(-1px);
}
[data-testid="stChatMessage"] {
    border: 1px solid #26365d;
    border-radius: 16px;
    padding: 14px;
    background: rgba(15, 25, 52, .75);
    animation: fadeIn .3s ease;
}
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(8px);}
    to {opacity: 1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)


def ask_ollama(messages):
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Python AI Assistant, a friendly coding tutor. "
                    "Explain concepts simply, give correct Python code, "
                    "use readable examples, and help debug errors. "
                    "If a question is unclear, ask a short clarification."
                )
            },
            *messages
        ],
        "stream": False
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=180
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def get_python_code(answer):
    blocks = re.findall(
        r"```(?:python|py)?\s*\n(.*?)```",
        answer,
        flags=re.DOTALL | re.IGNORECASE
    )
    return "\n\n".join(block.strip() for block in blocks)


def chat_as_text(messages):
    lines = ["Python AI Assistant Chat History", "=" * 35, ""]
    for message in messages:
        role = "You" if message["role"] == "user" else "AI Assistant"
        lines.append(f"{role}:\n{message['content']}\n")
    return "\n".join(lines)


with st.sidebar:
    st.markdown("## 🐍 Python AI Assistant")
    st.caption("LEARN • CODE • BUILD")
    st.divider()

    st.markdown("### ✨ Quick Prompts")

    quick_prompts = {
        "📘 Explain Python concepts": "Explain Python loops with simple examples.",
        "💻 Write a Python program": "Write a Python program to check whether a number is prime.",
        "🛠️ Debug my code": "Explain how to debug Python errors with an example.",
        "🎯 Interview questions": "Give me 10 beginner Python interview questions with answers."
    }

    for label, question in quick_prompts.items():
        if st.button(label, use_container_width=True):
            st.session_state.prompt = question

    st.divider()

    st.markdown("""
    <div class="status">
        <b>🟢 LOCAL AI</b><br><br>
        Ollama · Llama 3.2:1b
    </div>
    """, unsafe_allow_html=True)

    try:
        health = requests.get("http://localhost:11434/api/tags", timeout=2)
        if health.ok:
            st.caption("Ollama server reachable")
        else:
            st.caption("Ollama server needs attention")
    except requests.RequestException:
        st.caption("Ollama server not reachable")

    st.divider()

    if st.session_state.messages:
        st.download_button(
            "⬇️ Download Chat",
            data=chat_as_text(st.session_state.messages),
            file_name="python_ai_chat.txt",
            mime="text/plain",
            use_container_width=True
        )

        latest_code = ""
        for item in reversed(st.session_state.messages):
            if item["role"] == "assistant":
                latest_code = get_python_code(item["content"])
                if latest_code:
                    break

        if latest_code:
            st.download_button(
                "🐍 Download Latest Python Code",
                data=latest_code,
                file_name="generated_code.py",
                mime="text/x-python",
                use_container_width=True
            )

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.prompt = ""
        st.rerun()

    st.caption("Runs locally using Ollama.")


st.markdown("# 🐍 Python AI Assistant")
st.caption("Your personal AI coding tutor — learn, build and debug.")

if not st.session_state.messages:
    st.markdown("""
    <div class="hero">
        <h2>Welcome, Learner! ✨</h2>
        <p>
        Ask questions, learn Python, generate programs and understand
        coding errors — using a local AI model on your PC.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### What would you like to learn today?")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature">
            <h3>📘 Learn</h3>
            Understand Python concepts with examples.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature">
            <h3>💻 Build</h3>
            Generate programs and explore solutions.
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature">
            <h3>🛠️ Debug</h3>
            Understand errors and improve your code.
        </div>
        """, unsafe_allow_html=True)

for message in st.session_state.messages:
    avatar = "🧑‍💻" if message["role"] == "user" else "🐍"

    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

        if message["role"] == "assistant":
            code = get_python_code(message["content"])
            if code:
                st.download_button(
                    "⬇️ Download code",
                    data=code,
                    file_name="generated_code.py",
                    mime="text/x-python",
                    key=f"code_{st.session_state.messages.index(message)}"
                )

typed_prompt = st.chat_input("Ask about Python, code, or debugging...")
prompt = typed_prompt or st.session_state.prompt
st.session_state.prompt = ""

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🐍"):
        with st.spinner("Thinking with your local AI..."):
            try:
                answer = ask_ollama(st.session_state.messages)
                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

                code = get_python_code(answer)
                if code:
                    st.download_button(
                        "⬇️ Download code",
                        data=code,
                        file_name="generated_code.py",
                        mime="text/x-python",
                        key=f"new_code_{len(st.session_state.messages)}"
                    )

            except requests.exceptions.ConnectionError:
                st.error(
                    "Cannot connect to Ollama. Open another terminal "
                    "and run: ollama serve"
                )

            except requests.exceptions.Timeout:
                st.error(
                    "The model took too long to respond. Try a shorter "
                    "question or check whether Ollama is running."
                )

            except requests.exceptions.RequestException as error:
                st.error(f"Ollama request failed: {error}")

            except (KeyError, ValueError):
                st.error("Unexpected response from Ollama. Try again.")
