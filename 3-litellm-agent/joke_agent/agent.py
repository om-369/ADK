import os
import random

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

model = LiteLlm(
    model="openrouter/openai/gpt-3.5-turbo",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    )

def get_joke_agent():
    jokes=[
        "Why did the chicken cross the road? To get to the other side!",
        "What do you call a belt made of watches? A waist of time.",
        "What do you call fake spaghetti? An impasta!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        ]
    return random.choice(jokes)



root_agent=Agent(
    name="joke_agent",
    model=model,
    description="Joke Agent",
    instruction="""
    You are a helpful assistant that can tell jokes. only use the tool 'get_joke_agent' to tell jokes.
    """,
    tools=[get_joke_agent],
    )
