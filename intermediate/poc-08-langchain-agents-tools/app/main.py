"""
POC 8: LangChain Agents with Tools - Main Application

This FastAPI application implements a ReAct agent with custom tools
for task execution and reasoning.
"""

import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import get_settings
from app.models import (
    TaskRequest,
    TaskResponse,
    ToolsListResponse,
    ToolInfo,
    HealthResponse,
    ErrorResponse,
)
from app.agent_executor import AgentExecutorService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global settings
settings = get_settings()

# Global agent executor
agent_service: Optional[AgentExecutorService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources"""
    global agent_service

    # Startup
    logger.info("Starting POC 8: LangChain Agents with Tools")

    # Initialize agent service
    agent_service = AgentExecutorService()

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title="POC 8: LangChain Agents with Tools",
    description="ReAct agent with custom tools for intelligent task execution",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    tools_count = len(agent_service.tools) if agent_service else 0
    return HealthResponse(
        status="healthy",
        message="POC 8: LangChain Agents with Tools is running",
        available_tools=tools_count,
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        if agent_service is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Agent service not initialized"
            )

        tools_count = len(agent_service.tools)

        return HealthResponse(
            status="healthy",
            message="All systems operational",
            available_tools=tools_count,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )


@app.get("/tools", response_model=ToolsListResponse)
async def list_tools():
    """
    List all available tools.

    Returns:
        ToolsListResponse with list of tools
    """
    try:
        if agent_service is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Agent service not initialized"
            )

        tools_info = []
        for tool_name, tool_description in agent_service.get_available_tools():
            tool_info = ToolInfo(
                name=tool_name,
                description=tool_description,
                parameters={}
            )
            tools_info.append(tool_info)

        return ToolsListResponse(
            tools=tools_info,
            total_tools=len(tools_info),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing tools: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing tools: {str(e)}"
        )


@app.post("/execute", response_model=TaskResponse)
async def execute_task(request: TaskRequest):
    """
    Execute a task using the ReAct agent.

    The agent will:
    1. Analyze the task
    2. Determine which tools to use
    3. Execute actions step by step
    4. Return the final result

    Args:
        request: TaskRequest with task description

    Returns:
        TaskResponse with result and execution steps
    """
    try:
        if agent_service is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Agent service not initialized"
            )

        logger.info(f"Received task: {request.task[:100]}...")

        # Execute the task
        response = agent_service.execute_task(
            task=request.task,
            max_iterations=request.max_iterations,
            verbose=request.verbose,
        )

        if not response.success:
            logger.warning(f"Task failed: {response.result}")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing task: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            detail=str(exc),
        ).dict(),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
