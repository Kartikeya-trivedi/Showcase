from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class Portfolio(SQLModel, table=True):
   
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: str = Field(index=True) 
    job_id: str = Field(unique=True, index=True) 
    
    full_name: str
    email: Optional[str] = None
    
    content: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    
    theme_id: str = Field(default="modern_tech")
    deployed_url: Optional[str] = None
    is_published: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
     arbitrary_types_allowed = True