"""Project schemas for API validation."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Base project schema."""
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""
    git_repo_url: Optional[str] = None
    git_default_branch: str = "main"
    alm_project_id: Optional[str] = None


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    git_repo_url: Optional[str] = None
    git_default_branch: Optional[str] = None
    alm_project_id: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    id: int
    git_repo_url: Optional[str]
    git_default_branch: str
    alm_project_id: Optional[str]
    owner_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
