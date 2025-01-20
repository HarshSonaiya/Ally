import re
import json
import requests
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from transformers import pipeline, AutoTokenizer
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from googleapiclient.discovery import build
import os

# Download required NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

# API Keys Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

class GoogleSearchManager:
    def __init__(self, api_key: str, cse_id: str):
        self.api_key = api_key
        self.cse_id = cse_id
        self.service = build("customsearch", "v1", developerKey=api_key)

    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        try:
            results = []
            search_results = self.service.cse().list(
                q=query,
                cx=self.cse_id,
                num=num_results
            ).execute()

            if 'items' in search_results:
                for item in search_results['items']:
                    content = f"{item.get('title', '')}\n{item.get('snippet', '')}"
                    results.append({
                        'content': content,
                        'source': 'Google Search'
                    })
            return results
        except Exception as e:
            print(f"Error in Google search: {str(e)}")
            return []

class DocumentManager:
    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.documents = {}
        self.vector_stores = {}
        self.combined_vectorstore = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )

    def add_pdf(self, pdf_path: str) -> bool:
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                print(f"Error: File not found at {pdf_path}")
                return False

            loader = PyPDFLoader(str(pdf_path))
            documents = loader.load()

            texts = []
            full_text = []
            for doc in documents:
                cleaned_text = ' '.join(doc.page_content.split())
                chunks = self.text_splitter.split_text(cleaned_text)
                texts.extend(chunks)
                full_text.append(cleaned_text)

            vectorstore = FAISS.from_texts(texts, self.embeddings)

            doc_id = str(pdf_path.stem)
            self.documents[doc_id] = {
                'path': str(pdf_path),
                'name': pdf_path.name,
                'chunks': texts,
                'full_text': '\n'.join(full_text)
            }
            self.vector_stores[doc_id] = vectorstore

            self._update_combined_vectorstore()
            print(f"Successfully added PDF: {pdf_path.name}")
            return True

        except Exception as e:
            print(f"Error adding PDF: {str(e)}")
            return False

    def _update_combined_vectorstore(self):
        try:
            all_texts = []
            for doc_info in self.documents.values():
                all_texts.extend(doc_info['chunks'])

            if all_texts:
                self.combined_vectorstore = FAISS.from_texts(all_texts, self.embeddings)
        except Exception as e:
            print(f"Error updating combined vector store: {str(e)}")

    def get_relevant_content(self, query: str, threshold: float = 0.7) -> List[Dict]:
        if not self.combined_vectorstore:
            return []

        try:
            results = []
            docs_and_scores = self.combined_vectorstore.similarity_search_with_score(query, k=5)

            for doc, score in docs_and_scores:
                if score <= threshold:
                    results.append({
                        'content': doc.page_content,
                        'score': score,
                        'source': 'PDF'
                    })

            return results
        except Exception as e:
            print(f"Error retrieving relevant content: {str(e)}")
            return []

    def list_documents(self) -> List[Dict]:
        """Return list of all documents with their details."""
        return [
            {'id': doc_id, 'name': info['name'], 'path': info['path']}
            for doc_id, info in self.documents.items()
        ]

    def get_document_by_id(self, doc_id: str) -> Optional[Dict]:
        """Get document information by ID."""
        return self.documents.get(doc_id)

class EnhancedSummarizer:
    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        self.model_name = model_name
        self.summarizer = pipeline("summarization", model=model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def clean_text(self, text: str) -> str:
        """Clean text by removing URLs, references, and contact information."""
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        # Remove social media references
        text = re.sub(r'@\w+', '', text)
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        # Remove phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '', text)
        # Remove follow/contact references
        text = re.sub(r'(?i)(follow us|contact us|call|visit|www|http).+', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text

    def summarize(self, text: str, summary_type: str = 'concise') -> str:
        if not text.strip():
            return "No content available for summarization."

        # Clean the text before summarization
        text = self.clean_text(text)

        ratios = {
            'concise': (0.1, 0.3),
            'detailed': (0.3, 0.6),
            'comprehensive': (0.5, 0.8)
        }
        min_ratio, max_ratio = ratios.get(summary_type, (0.1, 0.3))

        max_chunk_length = 1024
        chunks = self._split_text(text, max_chunk_length)
        summaries = []

        for chunk in chunks:
            input_length = len(self.tokenizer.encode(chunk))
            max_length = max(int(input_length * max_ratio), 50)
            min_length = max(int(input_length * min_ratio), 30)

            try:
                summary = self.summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
                summaries.append(summary[0]['summary_text'])
            except Exception as e:
                print(f"Error in summarization: {str(e)}")
                continue

        final_summary = ' '.join(summaries) if summaries else "Error generating summary."
        # Clean the summary again to ensure no unwanted content slips through
        return self.clean_text(final_summary)

    def _split_text(self, text: str, max_length: int) -> List[str]:
        """Split text into chunks of maximum token length."""
        tokens = self.tokenizer.encode(text)
        chunks = []
        current_chunk = []
        current_length = 0

        for token in tokens:
            if current_length >= max_length:
                chunks.append(self.tokenizer.decode(current_chunk))
                current_chunk = []
                current_length = 0
            current_chunk.append(token)
            current_length += 1

        if current_chunk:
            chunks.append(self.tokenizer.decode(current_chunk))

        return chunks

class AdvancedQuerySystem:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        self.doc_manager = DocumentManager(self.embeddings)
        self.summarizer = EnhancedSummarizer()
        self.google_search = GoogleSearchManager(GOOGLE_API_KEY, GOOGLE_CSE_ID)
        self.use_web_search = None

    def set_web_search_preference(self, use_web: bool):
        """Set user preference for web search"""
        self.use_web_search = use_web
        print(f"\nWeb search has been {'enabled' if use_web else 'disabled'}.")

    def process_query(self, query: str) -> Dict:
        try:
            # First check PDF results with a more lenient threshold
            pdf_results = self.doc_manager.get_relevant_content(query, threshold=0.9)  # Increased threshold to be more inclusive
            
            if pdf_results:
                # Sort results by score to get most relevant first
                pdf_results.sort(key=lambda x: x['score'])
                
                # Take up to top 3 most relevant results
                top_results = pdf_results[:3]
                
                # Check if results are too weak (all scores above 0.85)
                if all(result['score'] > 0.85 for result in top_results):
                    if self.use_web_search:
                        # Try web search as results are weak
                        google_results = self.google_search.search(query)
                        if google_results:
                            combined_text = ' '.join([result['content'] for result in google_results])
                            summary = self.summarizer.summarize(combined_text, 'concise')
                            return {
                                'source': 'Google Search (PDF results were too weak)',
                                'result': summary
                            }
                
                # Use PDF results even if somewhat weak
                combined_text = ' '.join([result['content'] for result in top_results])
                summary = self.summarizer.summarize(combined_text, 'concise')
                confidence_level = "high" if any(result['score'] < 0.7 for result in top_results) else "moderate"
                return {
                    'source': f'PDF (Confidence: {confidence_level})',
                    'result': summary
                }
            
            # If no PDF results at all and web search is enabled
            if self.use_web_search:
                google_results = self.google_search.search(query)
                if google_results:
                    combined_text = ' '.join([result['content'] for result in google_results])
                    summary = self.summarizer.summarize(combined_text, 'concise')
                    return {
                        'source': 'Google Search',
                        'result': summary
                    }
            
            # Only return no results if truly nothing found
            return {
                'source': 'System',
                'result': "No relevant information found in the documents. " + 
                        ("Consider enabling web search for broader results." if not self.use_web_search else 
                        "Try rephrasing your query to be more specific.")
            }

        except Exception as e:
            return {
                'source': 'Error',
                'result': f"Error processing query: {str(e)}"
        }

    def add_pdf_document(self, pdf_path: str):
        """Add a PDF document to the system."""
        return self.doc_manager.add_pdf(pdf_path)

    def summarize_pdf(self, doc_id: str, summary_type: str = 'concise') -> Dict:
        """Summarize a specific PDF document."""
        doc = self.doc_manager.get_document_by_id(doc_id)
        if not doc:
            return {
                'success': False,
                'message': f"Document with ID '{doc_id}' not found.",
                'summary': None
            }

        try:
            text = self.summarizer.clean_text(doc['full_text'])
            summary = self.summarizer.summarize(text, summary_type)
            return {
                'success': True,
                'message': 'Summary generated successfully.',
                'summary': summary,
                'document_name': doc['name']
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error generating summary: {str(e)}",
                'summary': None
            }

def main():
    system = AdvancedQuerySystem()

    while True:
        print("\n=== Advanced Query System Menu ===")
        print("1. Add PDF Document")
        print("2. Query Mode")
        print("3. Summarize PDF")
        print("4. List Documents")
        print("5. Toggle Web Search")
        print("6. Exit")
        choice = input("Enter your choice (1-6): ")

        if choice == '1':
            pdf_path = input("Enter PDF path: ")
            if system.add_pdf_document(pdf_path):
                # Only ask for web search preference after successful PDF addition
                if system.use_web_search is None:
                    while True:
                        web_choice = input("\nWould you like to enable web-based answers for queries not found in PDFs? (yes/no): ").lower()
                        if web_choice in ['yes', 'no']:
                            system.set_web_search_preference(web_choice == 'yes')
                            break
                        print("Please enter 'yes' or 'no'.")

        elif choice == '2':
            if not system.doc_manager.list_documents():
                print("Please add at least one PDF document before querying.")
                continue
                
            while True:
                query = input("\nEnter your query (or 'back' to return to the main menu): ")
                if query.lower() == 'back':
                    break
                result = system.process_query(query)
                print(f"\nSource: {result['source']}")
                print(f"Result: {result['result']}")

        elif choice == '3':
            documents = system.doc_manager.list_documents()
            if not documents:
                print("No documents available. Please add some PDFs first.")
                continue

            print("\nAvailable Documents:")
            for doc in documents:
                print(f"ID: {doc['id']} - Name: {doc['name']}")

            doc_id = input("\nEnter document ID to summarize: ")
            print("\nSummary Types:")
            print("1. Concise")
            print("2. Detailed")
            print("3. Comprehensive")
            summary_type = input("Choose summary type (1-3): ")
            
            summary_types = {
                '1': 'concise',
                '2': 'detailed',
                '3': 'comprehensive'
            }
            
            summary_result = system.summarize_pdf(
                doc_id, 
                summary_types.get(summary_type, 'concise')
            )

            if summary_result['success']:
                print(f"\nSummary of {summary_result['document_name']}:")
                print(summary_result['summary'])
            else:
                print(f"\nError: {summary_result['message']}")

        elif choice == '4':
            documents = system.doc_manager.list_documents()
            if not documents:
                print("No documents available. Please add some PDFs first.")
                continue

            print("\nLoaded Documents:")
            for doc in documents:
                print(f"ID: {doc['id']}")
                print(f"Name: {doc['name']}")
                print(f"Path: {doc['path']}")
                print("-" * 50)

        elif choice == '5':
            if system.use_web_search is None:
                print("Please add a PDF document first before configuring web search.")
                continue
                
            current_status = "enabled" if system.use_web_search else "disabled"
            print(f"\nWeb search is currently {current_status}")
            while True:
                choice = input("Would you like to toggle web search? (yes/no): ").lower()
                if choice in ['yes', 'no']:
                    if choice == 'yes':
                        system.set_web_search_preference(not system.use_web_search)
                    break
                print("Please enter 'yes' or 'no'.")

        elif choice == '6':
            print("\nThank you for using Advanced Query System. Goodbye!")
            break

        else:
            print("\nInvalid choice. Please enter a number between 1 and 6.")

if __name__ == "__main__":
    main()