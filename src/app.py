import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent)) 
from rag import generate_answer

st.set_page_config(page_title="FastAPI Docs Assistant", page_icon="\U0001F4D8") 
st.title("\U0001F4D8 FastAPI Docs Assistant")
st.caption("Ask questions about FastAPI. Answers are grounded in the official docs, with sources cited.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a question about FastAPI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching the docs..."):
            result = generate_answer(prompt, history=st.session_state.messages[:-1], k=6)
        st.markdown(result["answer"])
        with st.expander("View sources"):
            for i, s in enumerate(result["sources"], start=1):
                clean_section = s['section'].replace("`", "").replace("[", "").replace("]", "")
                st.markdown(f"**[{i}]** [{s['page_title']} - {clean_section}]({s['source_url']}) (relevance: {s['score']:.2f})")
                

    st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
