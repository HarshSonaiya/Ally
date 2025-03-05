import os
import logging
import openai
import re
import sys
from typing import List, Optional
from dotenv import load_dotenv
from PyPDF2 import PdfReader  

# Load environment variables
load_dotenv()

# Set OpenAI API key
api_key = "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"
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in environment variables.")
openai.api_key = api_key
openai.api_base = "https://openrouter.ai/api/v1"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SummaryType:
    EXECUTIVE = "executive"
    DETAILED = "detailed"
    BULLET_POINTS = "bullet_points"
    KEY_INSIGHTS = "key_insights"
    CUSTOM = "custom"

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a given PDF file."""
    try:
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return ""
        
        reader = PdfReader(pdf_path)
        return "".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        return ""

def chunk_text(text: str, chunk_size: int = 1024, overlap: int = 100) -> List[str]:
    """Split text into smaller chunks."""
    if not text:
        return []
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size - overlap)]

def decide_summary_type(text: str, user_request: Optional[str] = None) -> str:
    """Determine summary type."""
    request_lower = user_request.lower() if user_request else ""

    summary_mapping = {
        ("detailed summary", "comprehensive summary"): SummaryType.DETAILED,
        ("bullet points", "bullet list", "point-wise summary"): SummaryType.BULLET_POINTS,
        ("key insights", "important points", "major takeaways"): SummaryType.KEY_INSIGHTS,
        ("brief summary", "short summary", "executive summary"): SummaryType.EXECUTIVE,
        ("custom summary", "use this prompt"): SummaryType.CUSTOM,
    }
    
    for keywords, summary_type in summary_mapping.items():
        if any(phrase in request_lower for phrase in keywords):
            return summary_type
    
    return SummaryType.DETAILED  # Default to detailed

def get_summary_prompt(text: str, summary_type: Optional[str] = None, custom_prompt: Optional[str] = None) -> str:
    """Generate a summary prompt."""
    summary_type = summary_type or decide_summary_type(text)
    prompts = {
        SummaryType.EXECUTIVE: "Generate a concise executive summary:",
        SummaryType.DETAILED: "Create a comprehensive summary:",
        SummaryType.BULLET_POINTS: "Extract key points as a bullet-point list:",
        SummaryType.KEY_INSIGHTS: "Identify key insights:",
    }
    return f"{custom_prompt if summary_type == SummaryType.CUSTOM and custom_prompt else prompts.get(summary_type, prompts[SummaryType.DETAILED])}\n\n{text}"

def get_summary_with_llm(text: str, user_request: Optional[str] = None, max_length: int = 500) -> str:
    """Generate a summary using OpenRouter LLM."""
    try:
        summary_type = decide_summary_type(text, user_request)
        prompt = get_summary_prompt(text, summary_type)
        
        response = openai.ChatCompletion.create(
            model="mistralai/mistral-7b-instruct",
            messages=[
                {"role": "system", "content": "You are a helpful AI summarization assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=min(max_length, 1024),  # Ensure it's within model limits
            temperature=0.5
        )
        return response["choices"][0]["message"]["content"].strip()
    
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return "API error: Failed to generate summary."
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return "Unexpected error occurred."

def merge_summaries(summaries: List[str]) -> str:
    """Merge summarized chunks."""
    if not summaries:
        return ""
    sentences = re.split(r'(?<=[.!?])\s+', "\n\n".join(summaries))
    return " ".join(dict.fromkeys(sentences))  # Remove duplicates

def summarize_pdf(pdf_path: str, user_request: Optional[str] = None) -> str:
    """Summarize PDF content."""
    try:
        logger.info(f"Processing PDF: {pdf_path}")
        text = extract_text_from_pdf(pdf_path)
        if not text:
            return "No text found."
        
        summaries = [get_summary_with_llm(chunk, user_request) for chunk in chunk_text(text)]
        return merge_summaries(summaries)
    except Exception as e:
        logger.error(f"Error summarizing PDF: {str(e)}")
        return "Error summarizing PDF."

def main():
    """Run script from command line."""
    logger.info("Starting summarization...")
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "abc.pdf"
    user_request = sys.argv[2] if len(sys.argv) > 2 else ""
    
    summary = summarize_pdf(pdf_path, user_request)
    logger.info(f"Generated Summary:\n{summary}")

if __name__ == "__main__":
    main()