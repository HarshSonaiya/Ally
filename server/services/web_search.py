from typing import List, Dict
from googleapiclient.discovery import build
from transformers import pipeline, AutoTokenizer
from config import settings
import os
import re

class WebSearch:
    def __init__(self):
        self.cse_id = settings.GOOGLE_CSE_ID
        self.service = build("customsearch", "v1", developerKey=settings.GOOGLE_API_KEY)
        self.summarizer = pipeline("summarization", model=settings.SUMMARY_MODEL_NAME)
        self.tokenizer = AutoTokenizer.from_pretrained(settings.SUMMARY_MODEL_NAME)

    async def summarize(self, text: str, summary_type: str = 'concise') -> str:
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

    async def process_query(self, query: str, summary_type: str) -> Dict:
        try:
            google_results = self.search(query)
            if google_results:
                combined_text = ' '.join([result['content'] for result in google_results])
                summary = await self.summarize(combined_text, summary_type)
                return {
                    'source': 'Google Search',
                    'result': summary
                }
            else:
                return {
                    'source': 'Google Search',
                    'result': "No relevant information found. Try rephrasing your query to be more specific."
                }

        except Exception as e:
            return {
                'source': 'Error',
                'result': f"Error processing query: {str(e)}"
        }