from arcadepy import AsyncArcade
from dotenv import load_dotenv
from google.adk import Agent, Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService, Session
from google_adk_arcade.tools import get_arcade_tools
from google.genai import types
from human_in_the_loop import auth_tool, confirm_tool_usage

import os

load_dotenv(override=True)


async def main():
    app_name = "my_agent"
    user_id = os.getenv("ARCADE_USER_ID")

    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    client = AsyncArcade()

    agent_tools = await get_arcade_tools(
        client, toolkits=["GoogleHotels"]
    )

    for tool in agent_tools:
        await auth_tool(client, tool_name=tool.name, user_id=user_id)

    agent = Agent(
        model=LiteLlm(model=f"openai/{os.environ["OPENAI_MODEL"]}"),
        name="google_agent",
        instruction="# AI Agent for Hotel Search

## Introduction
This AI agent is designed to assist users in finding suitable hotels based on their travel preferences. By utilizing the Google Hotels API, the agent can search for hotels in specified locations, check availability, and provide a range of options based on user-defined criteria such as check-in and check-out dates, number of travelers, budget, and desired amenities.

## Instructions
1. Greet the user and ask for their hotel search criteria, including location, check-in and check-out dates, number of guests (adults and children), budget (minimum and maximum price), and any specific preferences.
2. Validate the user's input to ensure all required fields are filled.
3. Retrieve hotel search results using the Google Hotels API based on the user's criteria.
4. Present the user with the search results, including recommended hotels, prices, and any additional information they may find helpful.
5. If needed, allow users to refine their search parameters based on feedback or preferences.

## Workflows
### Workflow 1: Initial Hotel Search
1. Gather user input for:
   - Location
   - Check-in date
   - Check-out date
   - Number of adults and children
   - Minimum and maximum price (optional)
   - Specific preferences (optional)
2. Use the `GoogleHotels_SearchHotels` tool to fetch hotel results.

### Workflow 2: Refinement of Search 
1. Ask the user if they would like to refine their search based on the initial results.
2. If the user provides new search criteria:
   - Update relevant parameters (e.g., price range, dates).
3. Use the `GoogleHotels_SearchHotels` tool again with the refined parameters to get updated results.

### Workflow 3: Result Presentation
1. Present the user with the search results, highlighting essential information such as hotel names, prices, and amenities.
2. Optionally, provide links to view more details or booking options.
3. Ask the user if they need further assistance or if they would like to perform another search.",
        description="An agent that uses GoogleHotels tools provided to perform any task",
        tools=agent_tools,
        before_tool_callback=[confirm_tool_usage],
    )

    session = await session_service.create_session(
        app_name=app_name, user_id=user_id, state={
            "user_id": user_id,
        }
    )
    runner = Runner(
        app_name=app_name,
        agent=agent,
        artifact_service=artifact_service,
        session_service=session_service,
    )

    async def run_prompt(session: Session, new_message: str):
        content = types.Content(
            role='user', parts=[types.Part.from_text(text=new_message)]
        )
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=content,
        ):
            if event.content.parts and event.content.parts[0].text:
                print(f'** {event.author}: {event.content.parts[0].text}')

    while True:
        user_input = input("User: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        await run_prompt(session, user_input)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())