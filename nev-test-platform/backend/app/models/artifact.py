"""Artifact model for software versions from artifact repository."""
from sqlalchemy import String, Integer, Text, BigInteger, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
import enum

from .base import BaseModel


class ArtifactType(str, enum.Enum):
    """Artifact type enumeration."""
    FIRMWARE = "firmware"
    SOFTWARE = "software"
    BOOTLOADER = "bootloader"
    CALIBRATION = "calibration"
    CONFIG = "config"
    OTHER = "other"


class Artifact(BaseModel):
    """Artifact model for managing software versions."""
    __tablename__ = "artifacts"
    
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    artifact_type: Mapped[ArtifactType] = mapped_column(
        SQLEnum(ArtifactType), default=ArtifactType.SOFTWARE, nullable=False
    )
    
    # Repository info
    repository: Mapped[str] = mapped_column(String(200), nullable=False)
    group_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    artifact_id: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # File info
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # SHA256
    download_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    
    # Target device type
    target_device_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    release_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    build_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    branch: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    commit_hash: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    
    # Unique constraint
    __table_args__ = (
        # Unique combination of name and version
    )
    
    def __repr__(self) -> str:
        return f"<Artifact(id={self.id}, name={self.name}, version={self.version})>"
