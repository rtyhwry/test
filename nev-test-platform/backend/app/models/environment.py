"""Test environment model combining host and devices."""
from sqlalchemy import String, Integer, Text, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
import enum

from .base import BaseModel


class EnvironmentStatus(str, enum.Enum):
    """Environment status enumeration."""
    AVAILABLE = "available"
    LOCKED = "locked"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


class TestEnvironment(BaseModel):
    """Test environment model combining host and devices."""
    __tablename__ = "test_environments"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    
    # Project relationship
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False
    )
    project: Mapped["Project"] = relationship("Project", back_populates="environments")
    
    # Host relationship
    host_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("test_hosts.id"), nullable=False
    )
    host: Mapped["TestHost"] = relationship("TestHost", back_populates="environments")
    
    # Status
    status: Mapped[EnvironmentStatus] = mapped_column(
        SQLEnum(EnvironmentStatus), default=EnvironmentStatus.AVAILABLE, nullable=False
    )
    locked_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    locked_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    lock_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Configuration
    is_auto_release: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    max_lock_hours: Mapped[int] = mapped_column(Integer, default=24, nullable=False)
    
    # Description
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # JSON array
    
    # Relationships
    devices: Mapped[List["TestDevice"]] = relationship(
        "TestDevice", back_populates="environment"
    )
    tasks: Mapped[List["TestTask"]] = relationship(
        "TestTask", back_populates="environment"
    )
    executions: Mapped[List["TaskExecution"]] = relationship(
        "TaskExecution", back_populates="environment"
    )
    
    def __repr__(self) -> str:
        return f"<TestEnvironment(id={self.id}, name={self.name}, status={self.status})>"
