from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


class GoogleAuthRequest(BaseModel):
    code: str


class WorkspaceRequest(BaseModel):
    workspace_name: str


class AudioVideoFileRequest(BaseModel):
    # participants: List[str]
    workspace_name: str


class FileUploadRequest(BaseModel):
    workspace_name: str


class FileRetrievalResponse(BaseModel):
    file_id: str
    transcript: str
    participants: list
    embeddings: list | None = []


class TranscriptData(BaseModel):
    transcript: str
    participants: list
    embeddings: list | None = []


class SummarizationResponse(BaseModel):
    transcription: str
    topics: List[str]
    summaries: List[str]


class MailBody(BaseModel):
    body: str
    to: List[EmailStr]

class WebSearchRequest(BaseModel):
    query: str
    summary_type: str

class ClassifyQuery(BaseModel):
    query: str = Field(..., description="Extract the actual user query to respond to.")
    phrases: List[str] = Field(..., description="A list of extracted phrases from the user query tp search for while searching for news articles.")
    category: str = Field(..., description="The classified category of the user query. Possible values: 'General Query', 'Audio Files Related Query', 'PDF File Related Query', 'News Explain Query', 'Unknown Query'.")
    keywords: List[str] = Field(..., description="A list of extracted essential keywords from the user query.")
    start_timestamp: Optional[str] = Field(None, description="The extracted start timestamp if any, otherwise None.")
    end_timestamp: Optional[str] = Field(None, description="The extracted end timestamp if any, otherwise None.")
    