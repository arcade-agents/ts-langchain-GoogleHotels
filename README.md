# An agent that uses GoogleHotels tools provided to perform any task

## Purpose

# AI Agent for Hotel Search

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
3. Ask the user if they need further assistance or if they would like to perform another search.

## MCP Servers

The agent uses tools from these Arcade MCP Servers:

- GoogleHotels

## Getting Started

1. Install dependencies:
    ```bash
    bun install
    ```

2. Set your environment variables:

    Copy the `.env.example` file to create a new `.env` file, and fill in the environment variables.
    ```bash
    cp .env.example .env
    ```

3. Run the agent:
    ```bash
    bun run main.ts
    ```