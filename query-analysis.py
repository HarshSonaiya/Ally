import os
from googleapiclient.discovery import build
from PyPDF2 import PdfReader
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pdfplumber

# === API Configuration ===
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Google API key (GOOGLE_API_KEY) is not set. Please set the key before running the program.")

GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
if not GOOGLE_CSE_ID:
    raise ValueError("Google Custom Search Engine ID (GOOGLE_CSE_ID) is not set. Please set the ID before running the program.")

# === Models Initialization ===
similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
summarizer = pipeline("summarization", model="t5-small")

# === Helper Functions ===

def compute_similarity(query, pdf_chunks):
    """Compute similarity scores for query and multiple PDF chunks."""
    try:
        query_embedding = similarity_model.encode([query])
        pdf_embeddings = similarity_model.encode(pdf_chunks)  # Batch encode PDF chunks
        similarities = cosine_similarity(query_embedding, pdf_embeddings)
        return similarities[0]  # Return similarity scores for all chunks
    except Exception as e:
        return f"Error during similarity computation: {str(e)}"

def extract_relevant_text(query, pdf_text, threshold=0.3):
    """Extract the most relevant sections from the PDF based on query similarity."""
    try:
        # Split by paragraphs instead of sentences for better context capture
        pdf_chunks = pdf_text.split("\n\n")  # Splitting by double newline (paragraphs)
        similarities = compute_similarity(query, pdf_chunks)
        max_similarity_index = similarities.argmax()
        most_relevant_chunk = pdf_chunks[max_similarity_index]

        if similarities[max_similarity_index] > threshold:
            return most_relevant_chunk
        else:
            return "No relevant information found in the PDF."
    except Exception as e:
        return f"Error during relevance extraction: {str(e)}"

def summarize_text(text, min_length=30, max_length=None):
    """
    Summarize text using a pre-trained summarization model with dynamic length adjustment.
    """
    try:
        input_length = len(text.split())  # Calculate input length in words
        
        # Dynamically adjust max_length based on input length
        if max_length is None or max_length > input_length * 0.8:
            max_length = int(input_length * 0.8)
        if min_length >= max_length:
            min_length = int(max_length * 0.5)  # Ensure min_length is proportionally smaller

        summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return f"Error during summarization: {str(e)}"

def handle_web_search(query):
    """Handle Google web search for the query."""
    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        result = service.cse().list(q=query, cx=GOOGLE_CSE_ID).execute()
        items = result.get("items", [])
        if items:
            return "\n".join([f"{item['title']}: {item['link']}" for item in items[:3]])
        else:
            return "\nNo search results found."
    except Exception as e:
        return f"\nError during web search: {str(e)}"

def handle_answer_from_pdf(query, pdf_path):
    """Handle query and extract a summarized answer from PDF."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            pdf_text = " ".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        relevant_text = extract_relevant_text(query, pdf_text)
        summarized_text = summarize_text(relevant_text)
        return f"\nSummarized information from the PDF:\n{summarized_text}"
    except Exception as e:
        return f"\nError processing PDF: {str(e)}"

def handle_summarize(pdf_path, min_length=50, max_length=150):
    """Summarize the entire content of the PDF file."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            pdf_text = " ".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        if len(pdf_text) < min_length:
            return "The content is too short to summarize."
        summary = summarize_text(pdf_text, min_length=min_length, max_length=max_length)
        return f"\nSummarized PDF content:\n{summary}"
    except Exception as e:
        return f"\nError during summarization: {str(e)}"

def classify_intent(query, pdf_path=None):
    """Classify the user's intent based on the query."""
    query = query.strip().lower()
    if "summarize" in query:
        return "summarize"
    if pdf_path:  # Allow dynamic PDF intent classification
        with pdfplumber.open(pdf_path) as pdf:
            pdf_text = " ".join([page.extract_text() for page in pdf.pages if page.extract_text()])
            similarity = compute_similarity(query, [pdf_text])  # Compare query with entire PDF content
            if similarity[0] > 0.3:  # Dynamic threshold
                return "answer_from_pdf"
    return "web_search"

def handle_user_query(query, pdf_path=None):
    """Handle the user's query based on the detected intent."""
    try:
        intent = classify_intent(query, pdf_path)
        print(f"\n\nDetected Intent: {intent}")
        if intent == "web_search":
            return handle_web_search(query)
        elif intent == "answer_from_pdf" and pdf_path:
            return handle_answer_from_pdf(query, pdf_path)
        elif intent == "summarize" and pdf_path:
            return handle_summarize(pdf_path)
        else:
            return f"\nInvalid or unsupported intent for query: {query}"
    except Exception as e:
        return f"\nError handling query: {str(e)}"

if __name__ == "__main__":
    pdf_path = input("\nEnter the path to the PDF file: ")
    while True:
        query = input("\nEnter your query (or type 'exit' to quit): ")
        if query.lower() == 'exit':
            print("Exiting the program.")
            break
        response = handle_user_query(query, pdf_path=pdf_path)
        print(f"Response: {response}")
        print("-" * 50)