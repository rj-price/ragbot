# RAG Bot: Document Q&A

Document Q&A using RAG with OpenAI API, Docling, and LanceDB.

## Overview

RAG Bot is a Streamlit-based application that allows users to ask questions about uploaded documents. It uses Retrieval Augmented Generation (RAG) using the OpenAI API, Docling, and LanceDB to provide accurate and contextually relevant answers.

**Note**: An OpenAI API key is required for this tool to function. Without a valid API key, the tool will not be able to connect to the OpenAI services.

## Features

- Upload documents in PDF or DOCX format.
- Process and store documents in a LanceDB database.
- Ask questions about the uploaded documents.
- Retrieve relevant context from the documents.
- Generate responses using the OpenAI API.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/rj-price/ragbot.git
    cd ragbot
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up your `.env` file with your OpenAI API key and model of choice:
    ```bash
    cp .example.env .env
    ```

## Usage

1. Run the Streamlit application:
    ```bash
    streamlit run ragbot.py
    ```

2. Open your web browser and navigate to `http://localhost:8501`.

3. Use the sidebar to upload a document and select a database.

4. Ask questions about the document using the chat input.

## File Structure

- `ragbot.py`: Main application file.
- `utils/`: Directory containing utility functions for processing documents, retrieving context, and generating chat responses.
- `data/`: Directory where document databases are stored.

## Acknowledgements

- [Streamlit](https://streamlit.io/)
- [OpenAI](https://openai.com/)
- [LanceDB](https://lancedb.com/)
- [Docling](https://docling.com/)
