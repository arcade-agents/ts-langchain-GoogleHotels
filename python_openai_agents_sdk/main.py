from agents import (Agent, Runner, AgentHooks, Tool, RunContextWrapper,
                    TResponseInputItem,)
from functools import partial
from arcadepy import AsyncArcade
from agents_arcade import get_arcade_tools
from typing import Any
from human_in_the_loop import (UserDeniedToolCall,
                               confirm_tool_usage,
                               auth_tool)

import globals


class CustomAgentHooks(AgentHooks):
    def __init__(self, display_name: str):
        self.event_counter = 0
        self.display_name = display_name

    async def on_start(self,
                       context: RunContextWrapper,
                       agent: Agent) -> None:
        self.event_counter += 1
        print(f"### ({self.display_name}) {
              self.event_counter}: Agent {agent.name} started")

    async def on_end(self,
                     context: RunContextWrapper,
                     agent: Agent,
                     output: Any) -> None:
        self.event_counter += 1
        print(
            f"### ({self.display_name}) {self.event_counter}: Agent {
                # agent.name} ended with output {output}"
                agent.name} ended"
        )

    async def on_handoff(self,
                         context: RunContextWrapper,
                         agent: Agent,
                         source: Agent) -> None:
        self.event_counter += 1
        print(
            f"### ({self.display_name}) {self.event_counter}: Agent {
                source.name} handed off to {agent.name}"
        )

    async def on_tool_start(self,
                            context: RunContextWrapper,
                            agent: Agent,
                            tool: Tool) -> None:
        self.event_counter += 1
        print(
            f"### ({self.display_name}) {self.event_counter}:"
            f" Agent {agent.name} started tool {tool.name}"
            f" with context: {context.context}"
        )

    async def on_tool_end(self,
                          context: RunContextWrapper,
                          agent: Agent,
                          tool: Tool,
                          result: str) -> None:
        self.event_counter += 1
        print(
            f"### ({self.display_name}) {self.event_counter}: Agent {
                # agent.name} ended tool {tool.name} with result {result}"
                agent.name} ended tool {tool.name}"
        )


async def main():

    context = {
        "user_id": os.getenv("ARCADE_USER_ID"),
    }

    client = AsyncArcade()

    arcade_tools = await get_arcade_tools(
        client, toolkits=["GoogleHotels"]
    )

    for tool in arcade_tools:
        # - human in the loop
        if tool.name in ENFORCE_HUMAN_CONFIRMATION:
            tool.on_invoke_tool = partial(
                confirm_tool_usage,
                tool_name=tool.name,
                callback=tool.on_invoke_tool,
            )
        # - auth
        await auth_tool(client, tool.name, user_id=context["user_id"])

    agent = Agent(
        name="",
        instructions="# AI Agent for Hotel Search

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
        model=os.environ["OPENAI_MODEL"],
        tools=arcade_tools,
        hooks=CustomAgentHooks(display_name="")
    )

    # initialize the conversation
    history: list[TResponseInputItem] = []
    # run the loop!
    while True:
        prompt = input("You: ")
        if prompt.lower() == "exit":
            break
        history.append({"role": "user", "content": prompt})
        try:
            result = await Runner.run(
                starting_agent=agent,
                input=history,
                context=context
            )
            history = result.to_input_list()
            print(result.final_output)
        except UserDeniedToolCall as e:
            history.extend([
                {"role": "assistant",
                 "content": f"Please confirm the call to {e.tool_name}"},
                {"role": "user",
                 "content": "I changed my mind, please don't do it!"},
                {"role": "assistant",
                 "content": f"Sure, I cancelled the call to {e.tool_name}."
                 " What else can I do for you today?"
                 },
            ])
            print(history[-1]["content"])

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())