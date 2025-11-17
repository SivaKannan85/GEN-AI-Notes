"""
Agent executor using LangChain ReAct agent with custom tools.
"""

import logging
import time
from typing import List, Tuple
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.tools import Tool

from app.config import get_settings
from app.tools.calculator import get_calculator_tool
from app.tools.datetime_tool import get_datetime_tool
from app.tools.string_tools import get_string_tool
from app.tools.json_tool import get_json_tool
from app.tools.weather_tool import get_weather_tool
from app.models import AgentStep, TaskResponse

logger = logging.getLogger(__name__)

settings = get_settings()


class AgentExecutorService:
    """
    Service for executing tasks using LangChain agents with custom tools.
    """

    def __init__(self):
        """Initialize the agent executor service."""
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            openai_api_key=settings.openai_api_key,
        )

        # Initialize tools
        self.tools = self._initialize_tools()

        # Create the agent
        self.agent_executor = self._create_agent()

        logger.info(f"Initialized AgentExecutorService with {len(self.tools)} tools")

    def _initialize_tools(self) -> List[Tool]:
        """
        Initialize all available tools.

        Returns:
            List of Tool instances
        """
        tools = []

        if settings.enable_calculator:
            tools.append(get_calculator_tool())

        if settings.enable_datetime:
            tools.append(get_datetime_tool())

        if settings.enable_string_tools:
            tools.append(get_string_tool())
            tools.append(get_json_tool())

        # Always include weather tool for demonstration
        tools.append(get_weather_tool())

        logger.info(f"Initialized {len(tools)} tools: {[t.name for t in tools]}")

        return tools

    def _create_agent(self) -> AgentExecutor:
        """
        Create the ReAct agent with tools.

        Returns:
            AgentExecutor instance
        """
        # ReAct prompt template
        template = '''Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}'''

        prompt = PromptTemplate.from_template(template)

        # Create ReAct agent
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt,
        )

        # Create executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=settings.agent_verbose,
            max_iterations=settings.max_iterations,
            early_stopping_method=settings.agent_early_stopping_method,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )

        return agent_executor

    def execute_task(
        self,
        task: str,
        max_iterations: int = None,
        verbose: bool = None,
    ) -> TaskResponse:
        """
        Execute a task using the agent.

        Args:
            task: Task description
            max_iterations: Maximum iterations (overrides default)
            verbose: Enable verbose output (overrides default)

        Returns:
            TaskResponse with result and steps
        """
        try:
            start_time = time.time()

            logger.info(f"Executing task: {task}")

            # Update agent executor settings if provided
            if max_iterations is not None:
                self.agent_executor.max_iterations = max_iterations
            if verbose is not None:
                self.agent_executor.verbose = verbose

            # Execute the task
            result = self.agent_executor.invoke({"input": task})

            execution_time = time.time() - start_time

            # Extract steps
            steps = []
            if "intermediate_steps" in result:
                for i, (action, observation) in enumerate(result["intermediate_steps"]):
                    step = AgentStep(
                        step_number=i + 1,
                        thought=str(action.log).split("Action:")[0].replace("Thought:", "").strip() if "Action:" in str(action.log) else str(action.log),
                        action=action.tool,
                        action_input=str(action.tool_input),
                        observation=str(observation),
                    )
                    steps.append(step)

            # Build response
            response = TaskResponse(
                task=task,
                result=result.get("output", "No output generated"),
                steps=steps,
                total_steps=len(steps),
                success=True,
                execution_time_seconds=round(execution_time, 2),
            )

            logger.info(f"Task completed successfully in {execution_time:.2f}s with {len(steps)} steps")

            return response

        except Exception as e:
            logger.error(f"Task execution error: {str(e)}")

            execution_time = time.time() - start_time

            # Return error response
            return TaskResponse(
                task=task,
                result=f"Error: {str(e)}",
                steps=[],
                total_steps=0,
                success=False,
                execution_time_seconds=round(execution_time, 2),
            )

    def get_available_tools(self) -> List[Tuple[str, str]]:
        """
        Get list of available tools.

        Returns:
            List of (tool_name, tool_description) tuples
        """
        return [(tool.name, tool.description) for tool in self.tools]
