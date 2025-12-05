import asyncio
import os
import sys
from agents import Agent, Runner

# Mock Agent
class MockAgent:
    pass

async def test_runner_static():
    print("Testing Runner.run as static method...")
    try:
        # We can't easily mock the actual Runner.run behavior without the library, 
        # but we can check if we can pass it to to_thread
        
        # Actually, let's just try to call it directly with the real Agent if possible
        # or just inspect if it is callable
        
        print(f"Is Runner.run callable? {callable(Runner.run)}")
        
        # If I can run this script, I can try to fix the translator.py directly
        pass
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_runner_static())
