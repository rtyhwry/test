"""Project model for organizing test resources."""
from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional

from .base import BaseModel


class Project(BaseModel):
    """Project model for grouping test environments and tasks."""
    __tablename__ = "projects"
    
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    
    # Git repository configuration
    git_repo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    git_default_branch: Mapped[str] = mapped_column(String(100), default="main", nullable=False)
    
    # ALM configuration
    alm_project_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Owner
    owner_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    
    # Relationships
    environments: Mapped[List["TestEnvironment"]] = relationship(
        "TestEnvironment", back_populates="project"
    )
    tasks: Mapped[List["TestTask"]] = relationship(
        "TestTask", back_populates="project"
    )
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, code={self.code})>"
