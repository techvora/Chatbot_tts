import os
import time
import streamlit as st
from utils.chat_manager import ChatManager
from utils.tts_manager import TextToSpeech


# Initialize session state
def initialize_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_module' not in st.session_state:
        st.session_state.current_module = "chat"
    if 'tts_enabled' not in st.session_state:
        st.session_state.tts_enabled = False
    if 'avatar_enabled' not in st.session_state:
        st.session_state.avatar_enabled = False


# Sidebar for module selection and settings
def sidebar():
    with st.sidebar:
        st.title("AI Assistant Settings")

        # Module selection
        st.session_state.current_module = st.sidebar.radio(
            "Select Module",
            ["Chat"]
        )

        on = st.toggle("Activate text to speech")

        if on:
            st.info("Text to speech activated!")
            st.session_state.tts_enabled = True
        else:
            st.session_state.tts_enabled = False

        st.info("""
        ### 🤖 BOT Buddy - Your AI Assistant

        **Capabilities:**
        - 💬 Natural conversation
        - 🌐 General knowledge and reasoning
        - 📢 Optional Text-to-Speech (TTS) output

        Active a text to speech from the sidebar to begin listening, or watching your assistant in action!
        """)

        # Clear history button
        if st.button("Clear Conversation History"):
            st.session_state.chat_history = []
            if 'chat_manager' in st.session_state:
                st.session_state.chat_manager.clear_history()


# Chat module
def chat_module():
    st.title("AI Chat Assistant")

    if 'chat_manager' not in st.session_state:
        st.session_state.chat_manager = ChatManager(st.session_state.get('selected_model', 'gemini-1.5-pro'))

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("Type your message here..."):
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        with st.spinner("Thinking..."):
            response = st.session_state.chat_manager.chat_function(prompt)

        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.session_state.chat_history.append({"role": "assistant", "content": response})

        # Display response
        with st.chat_message("assistant"):
            # Add TTS if enabled
            if st.session_state.tts_enabled:
                tts = TextToSpeech(voice_id=os.getenv("VOICE_ID"),)
                response = st.session_state.chat_manager.chat_function(prompt)
                audio = tts.text_to_speech(response)

                if audio:
                    tts.render_audio_ui(audio)

                def typewriter(text, speed=0.05):
                    placeholder = st.empty()
                    output = ""
                    for char in text:
                        output += char
                        placeholder.markdown(output, unsafe_allow_html=True)
                        time.sleep(speed)

                typewriter(response)

        st.rerun()


# Main app
def main():
    st.set_page_config(
        page_title="Chatbot",
        page_icon="🤖",
        layout="wide"
    )

    initialize_session_state()
    sidebar()

    # Module routing
    if st.session_state.current_module == "Chat":
        chat_module()


if __name__ == "__main__":
    main()
