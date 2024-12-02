import streamlit as st
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import chromadb

# Function to read webpage content from a URL
def read_webpage_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        # Extract text content from all <p> tags
        document = " ".join([p.get_text() for p in soup.find_all("p")])
        return document
    except requests.RequestException as e:
        st.error(f"Error reading webpage from {url}: {e}")
        return None
    except Exception as e:
        st.error(f"Error processing the webpage: {e}")
        return None

# Function to generate embeddings
def generate_embeddings(text):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode([text])
    return embeddings[0]

# Function to store embeddings in ChromaDB
def store_in_chromadb(embedding, document_id, metadata):
    client = chromadb.Client()
    # Create a collection (or get it if it exists)
    collection = client.get_or_create_collection("webpage_embeddings")

    # Add the embedding to the collection with associated metadata
    collection.add(
        ids=[document_id],  # Unique ID for each document
        documents=[metadata["title"]],
        embeddings=[embedding.tolist()],
        metadatas=[metadata]
    )
    st.success(f"Embedding for '{metadata['title']}' stored in ChromaDB!")

# Streamlit App
st.title("Webpage Embeddings to ChromaDB")

# List of URLs (work_url preferred, fallback to DOI_URL)
urls = [
    "https://doi.org/10.1080/0144929X.2022.2105745",
    "https://www.worldcat.org/isbn/9789972236853",
    "https://doi.org/10.1002/aic.16927",
    "http://arxiv.org/abs/1608.01940",
    "https://doi.org/10.1002/ange.201712818",
    "https://doi.org/10.1002/ange.202115087",
    "https://doi.org/10.1002/anie.201712818",
    "https://doi.org/10.1002/anie.202115087",
    "http://arxiv.org/abs/quant-ph/0104136",
    "http://arxiv.org/abs/hep-ph/9610305"
]

# Process each URL
for index, url in enumerate(urls):
    st.subheader(f"Processing URL {index + 1}")
    st.write(f"Fetching content from: {url}")
    
    # Fetch content from the URL
    content = read_webpage_from_url(url)
    if content:
        st.text_area("Fetched Content", content[:500] + "...")  # Display first 500 characters
        
        # Generate embeddings
        st.write("Generating embeddings...")
        embedding = generate_embeddings(content)
        
        # Store embeddings in ChromaDB
        metadata = {
            "title": f"Document {index + 1}",
            "url": url,
            "document_id": f"doc_{index + 1}"
        }
        store_in_chromadb(embedding, metadata["document_id"], metadata)

st.write("Processing complete!")

