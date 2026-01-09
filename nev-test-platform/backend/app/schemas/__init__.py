"""Pydantic schemas package."""
from .user import UserCreate, UserUpdate, UserResponse, UserLogin, Token
from .project import ProjectCreate, ProjectUpdate, ProjectResponse
from .host import TestHostCreate, TestHostUpdate, TestHostResponse
from .device import TestDeviceCreate, TestDeviceUpdate, TestDeviceResponse
from .environment import TestEnvironmentCreate, TestEnvironmentUpdate, TestEnvironmentResponse
from .artifact import ArtifactCreate, ArtifactResponse
from .task import (
    TestTaskCreate, TestTaskUpdate, TestTaskResponse,
    TaskExecutionResponse, ExecuteTaskRequest
)
from .testcase import TestCaseCreate, TestCaseUpdate, TestCaseResponse, TestCaseResultResponse
from .report import TestReportResponse
from .common import PaginatedResponse, MessageResponse

__all__ = [
    # User
    "UserCreate", "UserUpdate", "UserResponse", "UserLogin", "Token",
    # Project
    "ProjectCreate", "ProjectUpdate", "ProjectResponse",
    # Host
    "TestHostCreate", "TestHostUpdate", "TestHostResponse",
    # Device
    "TestDeviceCreate", "TestDeviceUpdate", "TestDeviceResponse",
    # Environment
    "TestEnvironmentCreate", "TestEnvironmentUpdate", "TestEnvironmentResponse",
    # Artifact
    "ArtifactCreate", "ArtifactResponse",
    # Task
    "TestTaskCreate", "TestTaskUpdate", "TestTaskResponse",
    "TaskExecutionResponse", "ExecuteTaskRequest",
    # TestCase
    "TestCaseCreate", "TestCaseUpdate", "TestCaseResponse", "TestCaseResultResponse",
    # Report
    "TestReportResponse",
    # Common
    "PaginatedResponse", "MessageResponse",
]
