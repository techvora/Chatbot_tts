import os
import time
import streamlit as st
from utils.chat_manager import ChatManager
from utils.tts_manager import TextToSpeech
from utils.avatar_manager import AvatarManager


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
            ["Chat", "Avatar"]
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
        - 🧑‍🎤 Image to talking Avatar Generation

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
                tts = TextToSpeech(voice_id=os.getenv("VOICE_ID"), )
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


# avatar module
def avatar_module():
    if 'avatar_module' not in st.session_state:
        st.session_state.avatar_module = AvatarManager()

    st.title("HeyGen Avatar Video Generator")

    with st.sidebar:
        spinner_placeholder = st.empty()

    # Store selected image in session state
    if "selected_avatar" not in st.session_state:
        st.session_state.selected_avatar = None
    if "script" not in st.session_state:
        st.session_state.script = None
    if "voice_id" not in st.session_state:
        st.session_state.voice_id = None
    if "video_id" not in st.session_state:
        st.session_state.video_id = None
    if "video_url" not in st.session_state:
        st.session_state.video_url = None
    if "avatar_list" not in st.session_state:
        st.session_state.avatar_list = []

    col1, col2 = st.columns(2)

    with col1:
        option = st.selectbox("Generate video with..", ["New Avatar", "Existing Avatar"])
        st.session_state.script = st.text_area("Script Text",
                                               value="Hey my self Talking Photo Avatar, i'm Ai powered Avatar here to help you. ")

    with col2:
        if option == "Existing Avatar":
            selected_avatar = st.text_input("Paste photo ID here:", key="selected_avatar_id")
            if selected_avatar:
                st.session_state.selected_avatar = selected_avatar
            else:
                st.warning("No avatar ID provided enter photo id for further process.")

        elif option == "New Avatar" and st.session_state.script is not None:
            image_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
            if image_file is not None:
                with st.spinner("Uploading image..."):
                    with st.sidebar:
                        spinner_placeholder.info("⏳ Uploading image...")
                    st.session_state.selected_avatar = st.session_state.avatar_module.upload_image(image_file)

        generate = st.button("Generate Avatar Video")

    if option == "Existing Avatar" and st.session_state.script is not None:
        avatars = st.session_state.avatar_module.get_avatar()

        # Grid layout: 3 avatars per row
        columns_per_row = 4
        st.session_state.avatar_list = avatars.get("talking_photos", [])[:8]
        if st.session_state.avatar_list:
            for i in range(0, len(st.session_state.avatar_list), columns_per_row):
                cols = st.columns(columns_per_row)
                for idx, avatar in enumerate(st.session_state.avatar_list[i:i + columns_per_row]):
                    with cols[idx]:
                        st.image(avatar["preview_image_url"], width=200, caption=avatar["talking_photo_name"])
                        st.code(avatar["talking_photo_id"], language="text")

    if st.session_state.script is not None and st.session_state.selected_avatar is not None:
        if generate:
            with st.spinner("Retrieving voice ID..."):
                with st.sidebar:
                    spinner_placeholder.info("⏳ Retrieving voice ID...")
                # st.session_state.voice_id = st.session_state.avatar_module.get_voice_id()
                st.session_state.voice_id = "1985984feded457b9d013b4f6551ac94"

            if st.session_state.voice_id is not None:
                with st.spinner("Generating video..."):
                    with st.sidebar:
                        spinner_placeholder.info("⏳ Generating video...")
                    st.session_state.video_id = st.session_state.avatar_module.generate_video(st.session_state.selected_avatar, st.session_state.script, st.session_state.voice_id)

                if st.session_state.video_id is not None:
                    with st.spinner("Fetching video URL..."):
                        with st.sidebar:
                            spinner_placeholder.info("⏳ Fetching video URL...")
                        st.session_state.video_url = st.session_state.avatar_module.get_video_url(st.session_state.video_id)

                    if st.session_state.video_url is not None:
                        st.video(st.session_state.video_url)
                        st.write(st.session_state.video_url)
                    else:
                        st.error("Failed to retrieve video URL.")
                else:
                    st.error("Failed to retrieve video ID.")
            else:
                st.error("Failed to retrieve voice ID.")
    else:
        st.warning("Please upload an image and enter script text.")


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
    if st.session_state.current_module == "Avatar":
        avatar_module()


if __name__ == "__main__":
    main()
