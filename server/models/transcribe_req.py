from pydantic import BaseModel, EmailStr
from typing import List

class FileUploadRequest(BaseModel):
    file_path: str

class SummarizationResponse(BaseModel):
    transcription: str
    topics: List[str]
    summaries: List[str]

class MailBody (BaseModel):
    body: str
    to: List[EmailStr]