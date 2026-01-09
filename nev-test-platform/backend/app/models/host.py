"""Test host model for remote test execution machines."""
from sqlalchemy import String, Integer, Text, Boolean, Enum as SQLEnum, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
import enum

from .base import BaseModel


class HostStatus(str, enum.Enum):
    """Host status enumeration."""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    MAINTENANCE = "maintenance"


class HostOS(str, enum.Enum):
    """Host operating system enumeration."""
    LINUX = "linux"
    WINDOWS = "windows"
    MACOS = "macos"


class TestHost(BaseModel):
    """Test host model for machines that execute tests."""
    __tablename__ = "test_hosts"
    
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hostname: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)  # IPv4 or IPv6
    ssh_port: Mapped[int] = mapped_column(Integer, default=22, nullable=False)
    ssh_username: Mapped[str] = mapped_column(String(50), default="root", nullable=False)
    ssh_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Encrypted
    ssh_key_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # System info
    os_type: Mapped[HostOS] = mapped_column(
        SQLEnum(HostOS), default=HostOS.LINUX, nullable=False
    )
    os_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    cpu_cores: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    memory_gb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    disk_gb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Status
    status: Mapped[HostStatus] = mapped_column(
        SQLEnum(HostStatus), default=HostStatus.OFFLINE, nullable=False
    )
    last_heartbeat: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Workspace configuration
    workspace_path: Mapped[str] = mapped_column(
        String(500), default="/home/test/workspace", nullable=False
    )
    
    # Tags and description
    tags: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # JSON array
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    environments: Mapped[List["TestEnvironment"]] = relationship(
        "TestEnvironment", back_populates="host"
    )
    
    def __repr__(self) -> str:
        return f"<TestHost(id={self.id}, name={self.name}, ip={self.ip_address}, status={self.status})>"
