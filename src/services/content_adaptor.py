from agents import Agent, Runner
from src.core.config import settings
from src.models.user import UserInDB

class ContentAdaptor:
    def __init__(self):
        self.agent = Agent(
            name="Content Adaptor",
            instructions="You are an AI assistant that personalizes textbook content for a user.",
            model="gpt-4o",
        )

    async def personalize_content(self, chapter_content: str, user_profile: UserInDB) -> str:
        user_background_info = f"Software Background: {user_profile.software_background or 'N/A'}. Hardware Background: {user_profile.hardware_background or 'N/A'}."

        input_text = f"""
Adapt the following chapter content for a user with the following background:
{user_background_info}

Original Chapter Content: {chapter_content}

Personalized Content:
"""
        result = await Runner.run(self.agent, input=input_text)
        return str(result.final_output)