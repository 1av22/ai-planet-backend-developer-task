import spacy
import numpy as np
import faiss
from unstructured.partition.auto import partition
from unstructured.partition.text import partition_text
from unstructured.partition.docx import partition_docx
from unstructured.partition.pptx import partition_pptx
import pandas as pd
from typing import Dict

# Function to parse documents based on their file type


def parse_document(file_path: str, file_type: str) -> Dict[str, str]:
    try:
        if file_type == "application/pdf":
            elements = partition(filename=file_path)
        elif file_type == "text/plain":
            elements = partition_text(filename=file_path)
        elif file_type == "text/csv":
            df = pd.read_csv(file_path)
            text = df.to_string()
            elements = [{'text': text}]
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            elements = partition_docx(filename=file_path)
        elif file_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
            elements = partition_pptx(filename=file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        text = "\n".join([str(element) for element in elements])

        # Safely extract metadata if present
        metadata = {}
        for element in elements:
            if hasattr(element, 'metadata') and element.metadata:
                for key, value in vars(element.metadata).items():
                    if key and not key.startswith('__') and value is not None:
                        metadata[key] = str(value)

        return {"text": text, "metadata": metadata}

    except Exception as e:
        raise ValueError(f"Error parsing document: {e}")


# Function to create embeddings and add them to a FAISS index
def create_embeddings_and_index(doc_text: str, openai_api_key: str) -> faiss.Index:
    # Use spaCy with transformers for faster, lightweight embeddings
    nlp = spacy.load('en_core_web_md')  # A smaller spaCy model
    chunk_size = 2048  # Define based on the max token limit
    doc_chunks = [doc_text[i:i + chunk_size]
                  for i in range(0, len(doc_text), chunk_size)]

    # Generate embeddings for each chunk using spaCy's transformer
    embeddings = []
    for chunk in doc_chunks:
        doc = nlp(chunk)
        embedding = doc.vector  # Get the vector for the chunk
        embeddings.append(embedding)

    # Convert embeddings to a numpy array
    embeddings = np.array(embeddings)

    # Create FAISS index
    dimension = embeddings.shape[1]
    faiss_index = faiss.IndexFlatL2(dimension)  # L2 distance metric for FAISS

    # Add the embeddings to the FAISS index
    faiss_index.add(embeddings)

    return faiss_index
