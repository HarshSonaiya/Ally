from pydantic import BaseModel, EmailStr
from typing import List

class GoogleAuthRequest(BaseModel):
    code: str  

class WorkspaceRequest(BaseModel):
    workspace_name: str

class AudioVideoFileRequest(BaseModel):
    participants: List[str]
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


class MailBody (BaseModel):
    body: str
    to: List[EmailStr]