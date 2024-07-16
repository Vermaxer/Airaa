import streamlit as st
import requests
import logging
import time

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Streamlit setup
st.set_page_config(page_title="ChatBot UI", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to send query to API
def send_query(question):
    url = "http://localhost:3020/api/v1/prediction/81923407-56cb-4d94-b351-ff05efd2d66b"
    data = {
        "question": question
    }
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
        if i % 5 == 0:  # Update every 5 characters
            time.sleep(0.01)
    placeholder.markdown(full_response)
    return full_response

# Main Streamlit UI
def main():
    st.title("ChatBot UI")

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        # Display user message immediately
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Send query and get response
        with st.chat_message("assistant"):
            response = send_query(prompt)
            if "text" in response:
                full_response = simulate_streaming(response["text"])
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                logger.error(f"Unexpected response format: {response}")
                st.markdown("Sorry, I couldn't process that request.")

    # Sidebar options
    with st.sidebar:
        st.title("Options")
        if st.button("Clear Chat"):
            st.session_state.messages = []
            logger.debug("Chat cleared")

if __name__ == "__main__":
    main()