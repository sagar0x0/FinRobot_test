import streamlit as st
import autogen
from finrobot.utils import get_current_date, register_keys_from_json
from finrobot.agents.workflow import SingleAssistant
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize session state for message history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Streamlit UI setup
st.title("Market Forecaster Chatbot")

# Sidebar for API key input
st.sidebar.header("API Configuration")
oai_config_path = st.sidebar.text_input("OpenAI Config Path", value="/Users/sagar/Desktop/fin-ai/FinRobot_test/OAI_CONFIG_LIST")
finnhub_config_path = st.sidebar.text_input("Finnhub Config Path", value="/Users/sagar/Desktop/fin-ai/FinRobot_test/config_api_keys")

# Initialize SingleAssistant
@st.cache_resource
def get_assistant():
    llm_config = {
        "config_list": autogen.config_list_from_json(
            oai_config_path,
            filter_dict={"model": ["gpt-4-0125-preview"]},
        ),
        "timeout": 120,
        "temperature": 0,
    }
    register_keys_from_json(finnhub_config_path)
    return SingleAssistant("Market_Analyst", llm_config, human_input_mode="NEVER")

assistant = get_assistant()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input for user message
user_input = st.chat_input("Ask me anything about companies or the market:")

if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate assistant response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        with st.spinner("Thinking..."):
            response = assistant.chat(user_input)
            logging.debug(f"Raw response from assistant: {response}")
            
            # Extract the actual content from the response
            if isinstance(response, dict) and 'content' in response:
                response_content = response['content']
            elif isinstance(response, str):
                response_content = response
            else:
                response_content = str(response)

            logging.debug(f"Extracted response content: {response_content}")

        response_placeholder.markdown(response_content)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response_content})

# Add a button to clear the chat history
if st.button("Clear Chat History"):
    st.session_state.messages = []
    st.experimental_rerun()

# run cmd:   streamlit run /Users/sagar/Desktop/fin-ai/FinRobot_test/market_forcaster_ui.py


# to display-   all the "Market_Analyst (to User_Proxy): "
