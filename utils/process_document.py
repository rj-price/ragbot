import lancedb
import os
import streamlit as st
from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from typing import List
from .tokenizer import OpenAITokenizerWrapper

def process_document(doc):
    """Process a document and return the LanceDB database name."""
    
    tokenizer = OpenAITokenizerWrapper()  # Load custom tokenizer for OpenAI
    MAX_TOKENS = 8191  # text-embedding-3-large's maximum context length

    # Create temp directory
    if not os.path.exists("temp"):
        os.makedirs("temp")
    
    # Process file
    converter = DocumentConverter()
    
    try:
        file_path = os.path.join("temp", doc.name)
        with open(file_path, "wb") as f:
            f.write(doc.getbuffer())
        
        result = converter.convert(file_path)
        doc_name = os.path.splitext(os.path.basename(doc.name))[0]
        db_name = f"{doc_name}_db"
        
        os.remove(file_path)
    except Exception as e:
        st.error(f"Error processing {doc.name}: {str(e)}")
        return

    
    # Apply hybrid chunking
    chunker = HybridChunker(
        tokenizer=tokenizer,
        max_tokens=MAX_TOKENS,
        merge_peers=True,
    )

    chunk_iter = chunker.chunk(dl_doc=result.document)
    chunks = list(chunk_iter)

    # Create a LanceDB database
    db = lancedb.connect(f"data/{db_name}")

    # Get the OpenAI embedding function
    func = get_registry().get("openai").create(name="text-embedding-3-large")

    # Define a simplified metadata schema
    class ChunkMetadata(LanceModel):
        """
        You must order the fields in alphabetical order.
        This is a requirement of the Pydantic implementation.
        """

        filename: str | None
        page_numbers: List[int] | None
        title: str | None

    # Define the main Schema
    class Chunks(LanceModel):
        text: str = func.SourceField()
        vector: Vector(func.ndims()) = func.VectorField()  # type: ignore
        metadata: ChunkMetadata

    table = db.create_table("docling", schema=Chunks, mode="overwrite")

    # Create table with processed chunks
    processed_chunks = [
        {
            "text": chunk.text,
            "metadata": {
                "filename": chunk.meta.origin.filename,
                "page_numbers": [
                    page_no
                    for page_no in sorted(
                        set(
                            prov.page_no
                            for item in chunk.meta.doc_items
                            for prov in item.prov
                        )
                    )
                ]
                or None,
                "title": chunk.meta.headings[0] if chunk.meta.headings else None,
            },
        }
        for chunk in chunks
    ]

    # Add the chunks to the table (automatically embeds the text)
    table.add(processed_chunks)

    return db_name