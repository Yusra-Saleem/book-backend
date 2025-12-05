from agents import Agent, Runner
from src.core.config import settings
import asyncio

class Translator:
    def __init__(self):
        self.agent = Agent(
            name="Translator",
            instructions="You are a professional translator. Translate the following text accurately.",
            model="gpt-4o-mini",  # Using a faster model for chunked translation
        )

    async def translate_content(self, chapter_content: str, target_language: str = "Urdu") -> str:
        """
        Translates content by chunking it and processing chunks concurrently.
        """
        # 1. Split the content into chunks (e.g., by paragraph)
        chunks = [p.strip() for p in chapter_content.split('\n\n') if p.strip()]
        
        if not chunks:
            return ""

        # 2. Create a list of translation tasks
        tasks = []
        for chunk in chunks:
            input_text = f"""
Translate the following English text into {target_language}.
Do not add any extra commentary, just the translation.

English Text:
---
{chunk}
---

{target_language} Translation:
"""
            # Create a coroutine for each translation task
            tasks.append(self._translate_chunk(input_text))

        # 3. Run all translation tasks concurrently
        translated_chunks = await asyncio.gather(*tasks)

        # 4. Stitch the translated chunks back together
        return "\n\n".join(translated_chunks)

    async def _translate_chunk(self, input_text: str) -> str:
        """
        Sends a single chunk to the LLM for translation.
        """
        try:
            # Runner.run is an async static method
            result = await Runner.run(self.agent, input=input_text)
            
            # Ensure we return a string, even if the agent output is unexpected
            return str(result.final_output).strip() if result and result.final_output else ""
        except Exception as e:
            print(f"Warning: A translation chunk failed. Error: {e}")
            # Return an error message or the original text for the failed chunk
            return f"[Translation for this section failed: {str(e)}]"