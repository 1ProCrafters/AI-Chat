import streamlit as st
from hugchat import hugchat
from hugchat.login import Login
import spacy

nlp = spacy.load("en_core_web_sm")
print(spacy.u)

# App title
st.set_page_config(page_title=" HugChat")

# Hugging Face Credentials
with st.sidebar:
    st.title('🤗💬 HugChat')
    if ('EMAIL' in st.secrets) and ('PASS' in st.secrets):
        st.success('HuggingFace Login credentials already provided!', icon='✅')
        hf_email = st.secrets['EMAIL']
        hf_pass = st.secrets['PASS']
    else:
        hf_email = st.text_input('Enter E-mail:', type='password')
        hf_pass = st.text_input('Enter password:', type='password')
        if not (hf_email and hf_pass):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I help you?"}]
    st.session_state.context = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Function for generating LLM response
def generate_response(prompt_input, email, passwd):
    # Hugging Face Login
    sign = Login(email, passwd)
    cookies = sign.login()
    # Create ChatBot                        
    chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
    
    # Initialize conversation context
    if "context" not in st.session_state:
        st.session_state.context = {}
    
    # Update conversation context with previous messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            # Extract entities from user message
            entities = extract_entities(message["content"])
            for entity, value in entities.items():
                st.session_state.context[entity] = value
    
    # Generate response using conversation context
    response = chatbot.chat(prompt_input, context=st.session_state.context)
    st.session_state.context = chatbot.context
    
    return response

def extract_entities(message):
    doc = nlp(message)
    entities = {}
    for ent in doc.ents:
        entities[ent.label_] = ent.text
    return entities

# User-provided prompt
if prompt := st.chat_input(disabled=not (hf_email and hf_pass)):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_response(prompt, hf_email, hf_pass) 
            st.write(response) 
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)
