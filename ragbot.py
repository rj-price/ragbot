import lancedb
import os
import streamlit as st
from utils.process_document import process_document
from utils.get_context import get_context
from utils.get_chat_response import get_chat_response


# Initialize LanceDB connection
@st.cache_resource
def init_db(db_name):
    """Initialize database connection.

    Returns:
        LanceDB table object
    """
    db = lancedb.connect(f"data/{db_name}")
    return db.open_table("docling")


# ------------------------------------------------------------
# Initialize Streamlit app
# ------------------------------------------------------------

# Set page config
st.set_page_config(
    page_title="RAG Bot",
    page_icon="📚",
    initial_sidebar_state="expanded"
)

st.title("📚 RAG Bot: Document Q&A")

# Apply custom CSS styles
st.markdown(
    """
    <style>
    .stButton button { 
        float: right;
        background-color: #d3d3d3;
        color: black;
    }
    .search-result {
        margin: 10px 0;
        padding: 10px;
        border-radius: 4px;
        background-color: #f0f2f6;
    }
    .search-result summary {
        cursor: pointer;
        color: #0f52ba;
        font-weight: 500;
    }
    .search-result summary:hover {
        color: #1e90ff;
    }
    .metadata {
        font-size: 0.9em;
        color: black;
        font-style: italic;
    }
    .meta_text {
        font-size: 0.9em;
        color: gray;
    }
    </style>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    if st.button("New Chat", key="new_chat_button"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("")
    st.markdown("### Upload Document")
    
    uploaded_file = st.file_uploader("Upload a new document to create a new database:", type=["pdf", "docx"])

    if uploaded_file:
        if st.button("Process"):
            with st.spinner("Processing..."):
                process_document(uploaded_file)
            st.success("Processing successful")

    st.markdown("---")
    st.markdown("### Select Database")
    st.markdown("Select document database to query:")
    db_name = st.selectbox("Select a database", os.listdir("./data"))
    if db_name != "None":    
        table = init_db(db_name)
    else:
        st.error("No databases found. Please upload a document to create a new database.")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about the document"):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get relevant context
    with st.status("Searching document...", expanded=False) as status:
        context = get_context(prompt, table)

        st.write("Found relevant sections:")
        for chunk in context.split("\n\n"):
            # Split into text and metadata parts
            parts = chunk.split("\n")
            text = parts[0]
            metadata = {
                line.split(": ")[0]: line.split(": ")[1]
                for line in parts[1:]
                if ": " in line
            }

            source = metadata.get("Source", "Unknown source")
            title = metadata.get("Title", "Untitled section")

            st.markdown(
                f"""
                <div class="search-result">
                    <details>
                        <summary>{source}</summary>
                        <div class="metadata">Section: {title}</div>
                        <div class="meta_text" style="margin-top: 8px;">{text}</div>
                    </details>
                </div>
            """,
                unsafe_allow_html=True,
            )

    # Display assistant response first
    with st.chat_message("assistant"):
        # Get model response with streaming
        response = get_chat_response(st.session_state.messages, context)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
