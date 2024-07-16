import streamlit as st
import requests
import logging
import time
import uuid
import os
import streamlit.components.v1 as components
from uml import generate_diagram_prompt, create_diagram
from git import generate_documentation, push_to_github,analyze_repo
# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Streamlit setup
st.set_page_config(page_title="AIRA", layout="wide")

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())
if "editing" not in st.session_state:
    st.session_state.editing = None
if "mode" not in st.session_state:
    st.session_state.mode = "User"

# Function to send query to API
def send_query(question):
    url = "http://localhost:3020/api/v1/prediction/81923407-56cb-4d94-b351-ff05efd2d66b"
    data = {"question": question}
    logger.debug(f"Sending query: {data}")
    response = requests.post(url, json=data)
    logger.debug(f"Query response status: {response.status_code}")
    logger.debug(f"Query response content: {response.text}")
    return response.json()

# Function to simulate faster streaming
def simulate_streaming(text):
    placeholder = st.empty()
    full_response = ""
    for i in range(len(text)):
        full_response += text[i]
        placeholder.markdown(full_response + "▌")
        if i % 5 == 0:
            time.sleep(0.01)
    placeholder.markdown(full_response)
    return full_response

# Custom CSS (keep your existing CSS)
# Custom CSS
st.markdown("""
    <style>
    .stButton>button {
        background-color: transparent;
        color: #ffffff;
        border: none;
        padding: 5px 10px;
        font-size: 14px;
    }
    .chat-title {
        font-size: 16px;
        color: #ffffff;
        padding: 5px 0;
    }
    .sidebar-chat {
        width: 100%;
        padding: 10px;
        background-color: transparent;
        border: none;
        text-align: left;
        font-size: 14px;
    }
    .sidebar-chat:hover {
        background-color: rgba(255, 255, 255, 0.1);
    }
    .icon-button {
        background-color: transparent;
        border: none;
        color: #ffffff;
        cursor: pointer;
        font-size: 16px;
        opacity: 0.7;
    }
    .icon-button:hover {
        opacity: 1;
    }
    .selected-chat {
        background-color: rgba(255, 255, 255, 0.2);
    }
    .new-chat-button {
        border: 2px solid #4CAF50 !important;
        color: #4CAF50 !important;
        font-weight: bold !important;
        border-radius: 5px !important;
    }
    .clear-chat-button {
        background-color: #ff4b4b !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar for mode selection and chat history
with st.sidebar:
    st.markdown("### Mode Selection")
    mode = st.radio("Select Mode", ["User", "Developer", "UML"])
    st.session_state.mode = mode

    if mode in ["User", "Developer"]:
        st.markdown("### Chat History")
        if st.button("➕  New Chat", key="new_chat", help="Start a new chat", use_container_width=True):
            st.session_state.current_chat_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.experimental_rerun()
        
        for chat in st.session_state.chat_history:
            chat_title = chat['title'][:30] + "..." if len(chat['title']) > 30 else chat['title']
            button_class = "sidebar-chat selected-chat" if chat['id'] == st.session_state.current_chat_id else "sidebar-chat"
            if st.button(chat_title, key=chat['id'], help=chat['title'], use_container_width=True):
                st.session_state.current_chat_id = chat['id']
                st.session_state.messages = chat['messages']
                st.experimental_rerun()
        
        # Clear chat button
        st.markdown("<br>" * 5, unsafe_allow_html=True)
        if st.button("Clear Current Chat", key="clear_chat", use_container_width=True, help="Clear the current chat"):
            st.session_state.messages = []
            st.experimental_rerun()

# Main content area
st.title("AIra")

if st.session_state.mode == "UML":
    st.markdown("## UML Diagram Generator")
    diagram_types = ["class", "sequence", "usecase", "activity", "component", "state", "object", "deployment", "timing", "mindmap", "json", "yaml"]
    selected_diagrams = st.multiselect("Select diagram types to generate", diagram_types)
    custom_instructions = st.text_area("Custom instructions (optional)")
    
    if st.button("Generate Diagrams"):
        with st.spinner("Generating diagrams..."):
            for diagram_type in selected_diagrams:
                st.markdown(f"### Generating {diagram_type.capitalize()} Diagram")
                prompt = generate_diagram_prompt(diagram_type, custom_instructions)
                filename = create_diagram(diagram_type, prompt)
                if filename:
                    st.image(filename, caption=f"{diagram_type.capitalize()} Diagram")
                else:
                    st.error(f"Failed to generate {diagram_type} diagram")

else:  # User or Developer mode
    # Display chat messages
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            col1, col2 = st.columns([0.95, 0.05])
            with col1:
                if message["role"] == "user" and st.session_state.editing == i:
                    edited_message = st.text_input("Edit message", value=message["content"], key=f"edit_input_{i}")
                    if st.button("Save", key=f"save_{i}"):
                        message["content"] = edited_message
                        st.session_state.editing = None
                        st.experimental_rerun()
                else:
                    st.markdown(message["content"])
            with col2:
                if message["role"] == "user":
                    if st.button("✏️", key=f"edit_{i}", help="Edit", use_container_width=True):
                        st.session_state.editing = i
                        st.experimental_rerun()
                else:
                    if st.button("🔄", key=f"rephrase_{i}", help="Rephrase", use_container_width=True):
                        rephrased = send_query(f"Rephrase this more eloquently: {message['content']}")
                        if "text" in rephrased:
                            message["content"] = rephrased["text"]
                            st.experimental_rerun()

    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = send_query(prompt)
            if "text" in response:
                full_response = simulate_streaming(response["text"])
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                logger.error(f"Unexpected response format: {response}")
                st.markdown("Sorry, I couldn't process that request.")

        # Update chat history
        chat_exists = False
        for chat in st.session_state.chat_history:
            if chat['id'] == st.session_state.current_chat_id:
                chat['messages'] = st.session_state.messages
                chat['title'] = st.session_state.messages[0]['content'][:30] + "..."
                chat_exists = True
                break
        
        if not chat_exists:
            st.session_state.chat_history.append({
                'id': st.session_state.current_chat_id,
                'title': st.session_state.messages[0]['content'][:30] + "...",
                'messages': st.session_state.messages
            })

# Embed Flowise chatbot (only in User mode)
if st.session_state.mode == "User":
    with st.sidebar:
        components.html("""
        <div id="chatbot-container"></div>
        <script type="module">
            import Chatbot from 'https://cdn.jsdelivr.net/gh/vfa-phucnd/FlowiseChatEmbed@latest/dist/web.js'
            Chatbot.init({
                chatflowid: "81923407-56cb-4d94-b351-ff05efd2d66b",
                apiHost: "http://localhost:3020",
                chatflowConfig: {},
                theme: {
                    button: {
                        backgroundColor: "#3B81F6",
                        right: 20,
                        bottom: 20,
                        size: 'medium',
                        iconColor: 'white',
                    },
                    chatWindow: {
                        welcomeMessage: "Hello! How can I assist you today?",
                        backgroundColor: "#2A2A2A",
                        height: 550,
                        width: 350,
                        fontSize: 14,
                        poweredByTextColor: "#FFFFFF",
                        botMessage: {
                            backgroundColor: "#3A3A3A",
                            textColor: "#FFFFFF",
                            showAvatar: true,
                            avatarSrc: "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Google_Bard_logo.svg/1200px-Google_Bard_logo.svg.png",
                        },
                        userMessage: {
                            backgroundColor: "#3B81F6",
                            textColor: "#FFFFFF",
                            showAvatar: true,
                            avatarSrc: "https://icons.veryicon.com/png/o/miscellaneous/two-color-webpage-small-icon/user-244.png",
                        },
                        textInput: {
                            placeholder: "Type your question",
                            backgroundColor: "#3A3A3A",
                            textColor: "#FFFFFF",
                            sendButtonColor: "#3B81F6",
                        }
                    }
                }
            })
            .then(() => {
                const elementToModify = document.querySelector(".lite-badge span");
                if (elementToModify) {
                    elementToModify.style.color = "transparent";
                }
            });
        </script>
        """, height=650)

# GitHub authentication
GITHUB_TOKEN = "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"


if st.session_state.mode == "UML":
    st.markdown("## UML and Documentation Generator")
    
    repo_url = st.text_input("Enter GitHub repository URL")
    include_diagrams = st.checkbox("Include UML Diagrams in Documentation")
    
    if st.button("Generate Documentation"):
        if repo_url:
            try:
                with st.spinner("Analyzing repository and generating documentation..."):
                    st.text("Starting repository analysis...")
                    repo_data = analyze_repo(repo_url, GITHUB_TOKEN)
                    st.text("Repository analysis complete.")
                    
                    st.text("Generating documentation...")
                    documentation = generate_documentation(repo_url, include_diagrams, GITHUB_TOKEN)
                    st.text("Documentation generated successfully.")
                    
                    st.markdown(documentation)
                    
                    # Store the generated documentation in session state
                    st.session_state.documentation = documentation
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.error("Please enter a valid GitHub repository URL.")
    
    # Move the push button outside the Generate Documentation button
    if 'documentation' in st.session_state and st.session_state.documentation:
        if st.button("Push README to GitHub"):
            st.text("Pushing README to GitHub...")
            result = push_to_github(repo_url, st.session_state.documentation, GITHUB_TOKEN)
            if result:
                st.success("README.md pushed to GitHub successfully!")
            else:
                st.error("Failed to push README.md to GitHub. Check the logs for more information.")