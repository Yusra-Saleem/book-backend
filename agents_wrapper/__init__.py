from typing import Any
import os

from src.core.config import settings

try:
    # openai-agents package imports as 'agents'
    from agents import Agent as OpenAIAgent, Runner as AgentsRunner
    AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import openai-agents: {e}")
    print("Please install: pip install openai-agents")
    OpenAIAgent = None
    AgentsRunner = None
    AGENTS_AVAILABLE = False


class Agent:
    """
    Wrapper around openai-agents Agent class.
    Used by RAG and personalization services.
    """

    def __init__(self, name: str, instructions: str, model: str = "gpt-3.5-turbo"):
        if not AGENTS_AVAILABLE:
            raise RuntimeError(
                "openai-agents package is not installed. Please run: pip install openai-agents"
            )

        if not settings.OPENAI_API_KEY:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Please configure it in your environment."
            )

        # Set OpenAI API key as environment variable for openai-agents
        os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

        # Create agent using openai-agents package
        self._agent = OpenAIAgent(
            name=name,
            instructions=instructions,
            model=model,
        )
        self.name = name
        self.instructions = instructions
        self.model = model


class Runner:
    """
    Wrapper around openai-agents Runner class.
    Provides async-compatible interface.
    """

    @staticmethod
    async def run(agent: Agent, input: str) -> Any:
        if not AGENTS_AVAILABLE:
            raise RuntimeError(
                "openai-agents package is not installed. Please run: pip install openai-agents"
            )

        if not settings.OPENAI_API_KEY:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Please configure it in your environment."
            )

        try:
            print(f"Making OpenAI Agents API call with model: {agent.model}")
            print(f"API key preview: {settings.OPENAI_API_KEY[:8]}...{settings.OPENAI_API_KEY[-4:] if len(settings.OPENAI_API_KEY) > 12 else '***'}")

            # Set API key for this run
            os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

            # Use openai-agents Runner
            runner = AgentsRunner(agent._agent)
            
            # Run the agent (openai-agents Runner.run is synchronous, so we run it in executor)
            import asyncio
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, runner.run, input)

            # Extract content from result
            if hasattr(result, 'final_output'):
                content = str(result.final_output)
            elif hasattr(result, 'content'):
                content = str(result.content)
            elif isinstance(result, str):
                content = result
            else:
                content = str(result)
            
            if not content:
                raise RuntimeError("Empty response from OpenAI Agents API")

            class Result:
                def __init__(self, final_output: str):
                    self.final_output = final_output

            return Result(content)
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            
            print(f"OpenAI Agents Error - Type: {error_type}, Message: {error_msg}")
            
            # Check for specific OpenAI API errors
            if hasattr(e, 'status_code'):
                status_code = e.status_code
                print(f"OpenAI API Status Code: {status_code}")
                
                if status_code == 401:
                    raise RuntimeError(
                        "Invalid OpenAI API key. Please verify your OPENAI_API_KEY in the .env file. "
                        "Make sure the key starts with 'sk-' and is correct."
                    )
                elif status_code == 429:
                    if "quota" in error_msg.lower() or "insufficient_quota" in error_msg.lower():
                        raise RuntimeError(
                            "OpenAI API quota exceeded. Please check:\n"
                            "1. Visit https://platform.openai.com/account/billing to verify credits\n"
                            "2. Check if you're using the correct API key for the account with credits\n"
                            "3. Verify the account has available credits/usage limits"
                        )
                    else:
                        raise RuntimeError(
                            "OpenAI API rate limit exceeded. Please wait a moment and try again."
                        )
                elif status_code == 500:
                    raise RuntimeError(
                        "OpenAI API server error. Please try again later."
                    )
            
            # Fallback error handling
            if "insufficient_quota" in error_msg.lower() or "quota" in error_msg.lower():
                raise RuntimeError(
                    "OpenAI API quota exceeded. Please check:\n"
                    "1. Visit https://platform.openai.com/account/billing\n"
                    "2. Verify you're using the correct API key\n"
                    "3. Check account has available credits"
                )
            elif "invalid_api_key" in error_msg.lower() or "401" in error_msg:
                raise RuntimeError(
                    "Invalid OpenAI API key. Please check your OPENAI_API_KEY in the .env file."
                )
            elif "rate_limit" in error_msg.lower() or "429" in error_msg:
                raise RuntimeError(
                    "OpenAI API rate limit exceeded. Please wait a moment and try again."
                )
            else:
                raise RuntimeError(f"OpenAI Agents error ({error_type}): {error_msg}")
