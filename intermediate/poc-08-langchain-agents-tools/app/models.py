"""
Pydantic models for LangChain Agents with Tools system.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class TaskRequest(BaseModel):
    """Request to execute a task using the agent."""
    task: str = Field(..., min_length=1, max_length=1000, description="Task description for the agent")
    max_iterations: Optional[int] = Field(default=10, ge=1, le=20, description="Maximum agent iterations")
    verbose: Optional[bool] = Field(default=False, description="Enable verbose output")

    class Config:
        json_schema_extra = {
            "example": {
                "task": "Calculate the compound interest on $10,000 at 5% for 3 years",
                "max_iterations": 10,
                "verbose": False
            }
        }


class AgentStep(BaseModel):
    """Individual step taken by the agent."""
    step_number: int = Field(..., description="Step number")
    thought: str = Field(..., description="Agent's thought process")
    action: str = Field(..., description="Action to take")
    action_input: str = Field(..., description="Input to the action")
    observation: str = Field(..., description="Result of the action")

    class Config:
        json_schema_extra = {
            "example": {
                "step_number": 1,
                "thought": "I need to calculate compound interest",
                "action": "Calculator",
                "action_input": "10000 * (1 + 0.05) ** 3",
                "observation": "11576.25"
            }
        }


class TaskResponse(BaseModel):
    """Response after executing a task."""
    task: str = Field(..., description="Original task")
    result: str = Field(..., description="Final result from the agent")
    steps: List[AgentStep] = Field(default_factory=list, description="Steps taken by the agent")
    total_steps: int = Field(..., description="Total number of steps")
    success: bool = Field(..., description="Whether the task completed successfully")
    execution_time_seconds: float = Field(..., description="Execution time in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "task": "Calculate compound interest",
                "result": "The compound interest is $1,576.25",
                "steps": [],
                "total_steps": 3,
                "success": True,
                "execution_time_seconds": 1.23
            }
        }


class ToolInfo(BaseModel):
    """Information about an available tool."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Tool parameters")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Calculator",
                "description": "Useful for mathematical calculations",
                "parameters": {"expression": "string"}
            }
        }


class ToolsListResponse(BaseModel):
    """Response listing all available tools."""
    tools: List[ToolInfo] = Field(..., description="List of available tools")
    total_tools: int = Field(..., description="Total number of tools")

    class Config:
        json_schema_extra = {
            "example": {
                "tools": [],
                "total_tools": 5
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    message: str = Field(..., description="Status message")
    available_tools: int = Field(..., description="Number of available tools")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "message": "All systems operational",
                "available_tools": 5
            }
        }


class ErrorResponse(BaseModel):
    """Error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Agent execution failed",
                "detail": "Maximum iterations reached without solution"
            }
        }
