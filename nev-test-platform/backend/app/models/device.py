"""Test device model for ECU/VCU and other automotive devices."""
from sqlalchemy import String, Integer, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
import enum

from .base import BaseModel


class DeviceType(str, enum.Enum):
    """Device type enumeration."""
    ECU = "ecu"  # Electronic Control Unit
    VCU = "vcu"  # Vehicle Control Unit
    BMS = "bms"  # Battery Management System
    MCU = "mcu"  # Motor Control Unit
    TBOX = "tbox"  # Telematics Box
    IVI = "ivi"  # In-Vehicle Infotainment
    ADAS = "adas"  # Advanced Driver Assistance Systems
    OTHER = "other"


class DeviceStatus(str, enum.Enum):
    """Device status enumeration."""
    AVAILABLE = "available"
    IN_USE = "in_use"
    UPGRADING = "upgrading"
    OFFLINE = "offline"
    FAULTY = "faulty"


class TestDevice(BaseModel):
    """Test device model for automotive testing devices."""
    __tablename__ = "test_devices"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    device_type: Mapped[DeviceType] = mapped_column(
        SQLEnum(DeviceType), default=DeviceType.ECU, nullable=False
    )
    serial_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    
    # Version info
    hardware_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    software_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    firmware_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Connection info
    connection_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # CAN, Ethernet, USB, etc.
    connection_params: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON config
    
    # Status
    status: Mapped[DeviceStatus] = mapped_column(
        SQLEnum(DeviceStatus), default=DeviceStatus.OFFLINE, nullable=False
    )
    
    # Environment relationship
    environment_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("test_environments.id"), nullable=True
    )
    environment: Mapped[Optional["TestEnvironment"]] = relationship(
        "TestEnvironment", back_populates="devices"
    )
    
    # Description and metadata
    manufacturer: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # JSON array
    
    def __repr__(self) -> str:
        return f"<TestDevice(id={self.id}, name={self.name}, type={self.device_type}, sn={self.serial_number})>"
