import os
from typing import List, Optional, Tuple, Dict
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.schema import Document

# === API Configuration ===
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

if not HUGGINGFACE_API_TOKEN:
    raise ValueError(
        "HuggingFace API token not found. Please set the HUGGINGFACEHUB_API_TOKEN environment variable."
    )

# === Model Initialization ===
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)

llm = HuggingFaceHub(
    repo_id="google/flan-t5-base",
    huggingfacehub_api_token=HUGGINGFACE_API_TOKEN,
    model_kwargs={
        "temperature": 0.5,
        "max_length": 512,
        "truncation": True
    }
)

def clean_text(text: str) -> str:
    """Clean text by removing excessive whitespace and newlines."""
    # Replace multiple newlines with a single newline
    text = ' '.join(text.split())
    # Fix spacing after punctuation
    text = text.replace(' .', '.').replace(' ,', ',')
    # Add proper spacing for readability
    text = text.replace('.', '. ').replace(',', ', ')
    return text

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # Reduced chunk size for more granular matching
            chunk_overlap=100
        )
        self.vectorstore = None
        self.full_text = None

    def load_pdf(self, pdf_path: str) -> List:
        """Load and split PDF document."""
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        # Clean and concatenate all text
        cleaned_texts = [clean_text(doc.page_content) for doc in documents]
        self.full_text = "\n\n".join(cleaned_texts)
        
        # Create smaller chunks for better matching
        splits = []
        for doc in documents:
            cleaned_text = clean_text(doc.page_content)
            # Split into paragraphs
            paragraphs = [p.strip() for p in cleaned_text.split('\n\n') if p.strip()]
            
            for para in paragraphs:
                splits.append(Document(
                    page_content=para,
                    metadata={"source": pdf_path, "type": "pdf"}
                ))
        
        self.vectorstore = FAISS.from_documents(splits, embeddings)
        return splits

    def compute_similarity(self, query: str, k: int = 3) -> List[Tuple[float, str]]:
        """Compute similarity between query and PDF content, return top k matches."""
        if not self.vectorstore:
            return []
        
        # Get top k similar documents and scores
        docs_and_scores = self.vectorstore.similarity_search_with_score(query, k=k)
        
        # Return list of (score, content) tuples
        return [(score, clean_text(doc.page_content)) 
                for doc, score in docs_and_scores]

    def get_relevant_content(self, query: str, k: int = 3) -> List:
        """Get relevant content from PDF."""
        if not self.vectorstore:
            raise ValueError("No document loaded. Please load a PDF first.")
        return self.vectorstore.similarity_search(query, k=k)

    def summarize_content(self, text_or_docs) -> str:
        """Summarize the provided content."""
        if isinstance(text_or_docs, str):
            docs = self.text_splitter.split_text(text_or_docs)
        else:
            docs = text_or_docs
        
        chain = load_summarize_chain(llm, chain_type="map_reduce")
        return chain.run(docs)

class WebSearchManager:
    def __init__(self):
        self.ddg_search = DuckDuckGoSearchRun()
        self.wikipedia = WikipediaAPIWrapper()
        
        try:
            self.google_search = GoogleSearchAPIWrapper(
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                google_cse_id=os.getenv("GOOGLE_CSE_ID")
            )
        except Exception:
            self.google_search = None
    
    def search(self, query: str) -> str:
        results = []
        
        # Try DuckDuckGo
        try:
            ddg_result = self.ddg_search.run(query)
            results.append(f"=== DuckDuckGo Results ===\n{ddg_result}")
        except Exception as e:
            print(f"DuckDuckGo search failed: {e}")
        
        # Try Wikipedia
        try:
            wiki_result = self.wikipedia.run(query)
            results.append(f"=== Wikipedia Results ===\n{wiki_result}")
        except Exception as e:
            print(f"Wikipedia search failed: {e}")
        
        # Try Google if available
        if self.google_search:
            try:
                google_result = self.google_search.run(query)
                results.append(f"=== Google Results ===\n{google_result}")
            except Exception as e:
                print(f"Google search failed: {e}")
        
        return "\n\n".join(results) if results else "No search results found."

class QueryHandler:
    def __init__(self):
        self.doc_processor = DocumentProcessor()
        self.web_searcher = WebSearchManager()
        self.current_pdf = None
        self.similarity_threshold = 0.5

    def load_pdf(self, pdf_path: str):
        """Load a new PDF document."""
        self.current_pdf = pdf_path
        return self.doc_processor.load_pdf(pdf_path)

    def handle_query(self, query: str, force_web: bool = False) -> Dict:
        """Process user query and return results from PDF and web."""
        try:
            results = {
                'sources': [],
                'answers': [],
                'similarity_scores': []
            }

            # If PDF is loaded and not forcing web search
            if self.current_pdf and not force_web:
                pdf_matches = self.doc_processor.compute_similarity(query)
                for score, content in pdf_matches:
                    if score > self.similarity_threshold:
                        results['sources'].append('pdf')
                        results['answers'].append(content)
                        results['similarity_scores'].append(score)

            # If no good PDF matches or forcing web search
            if not results['answers'] or force_web:
                web_result = clean_text(self.web_searcher.search(query))
                results['sources'].append('web')
                results['answers'].append(web_result)
                results['similarity_scores'].append(1.0)  # Default score for web results

            return results

        except Exception as e:
            return {
                'sources': ['error'],
                'answers': [f"Error processing query: {str(e)}"],
                'similarity_scores': [0.0]
            }

def main():
    handler = QueryHandler()
    
    while True:
        print("\n" + "="*50)
        print("Query System")
        print("="*50)
        print("\nOptions:")
        print("1. Load PDF")
        print("2. Query (Auto-decides between PDF and Web)")
        print("3. Force Web Search")
        print("4. Summarize Current PDF")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1":
            pdf_path = input("Enter the path to the PDF file: ")
            try:
                handler.load_pdf(pdf_path)
                print("\nSuccess: PDF loaded successfully!")
            except Exception as e:
                print(f"\nError: Failed to load PDF - {e}")

        elif choice == "2":
            query = input("Enter your query: ")
            results = handler.handle_query(query)
            
            print("\n" + "="*50)
            print("Query Results")
            print("="*50)
            
            # Display main results
            for idx, (source, answer, score) in enumerate(
                zip(results['sources'], results['answers'], results['similarity_scores']), 1
            ):
                print(f"\nResult {idx}:")
                print(f"Source: {source.upper()}")
                print(f"Confidence Score: {score:.2f}")
                print("-" * 30)
                print(answer)

        elif choice == "3":
            query = input("Enter your web search query: ")
            results = handler.handle_query(query, force_web=True)
            print("\nWeb Search Results:")
            print("-" * 30)
            for answer in results['answers']:
                print(answer)

        elif choice == "4":
            if not handler.current_pdf:
                print("\nError: No PDF loaded. Please load a PDF first!")
                continue
            try:
                summary = handler.doc_processor.summarize_content(handler.doc_processor.full_text)
                print("\nPDF Summary:")
                print("-" * 30)
                print(clean_text(summary))
            except Exception as e:
                print(f"\nError generating summary: {e}")

        elif choice == "5":
            print("\nThank you for using the Query System. Goodbye!")
            break
        
        else:
            print("\nError: Invalid choice. Please try again.")

if __name__ == "__main__":
    main()