# Setting Up GPT Actions for GoalGPT

This guide explains how to create a custom GPT that interacts with your GoalGPT API.

## Create a Custom GPT

1. Go to [https://chat.openai.com/](https://chat.openai.com/)
2. Click on "Create a GPT"
3. Configure the GPT:
   - Name: "Goal Manager"
   - Description: "I help you manage your hierarchical goals by interacting with the GoalGPT API."
   - Instructions: Include the following instructions:
     ```
     You are a goal management assistant that helps users organize their goals. You can:
     - List goals from the GoalGPT API
     - Create new goals
     - Update goal status (todo/doing/done)
     - Delete goals
     
     Always be helpful, direct, and efficient in managing the user's goals.
     
     When listing goals, format them in a hierarchical structure with appropriate indentation and status indicators:
     - ◯ Todo goals (grey)
     - ◉ In-progress goals (blue)
     - ✓ Completed goals (green)
     ```

## Configure Actions (Tool Calling)

1. Under "Actions," click "Add actions"
2. Configure the OpenAPI specification:
   - Authentication: API Key in Header
   - API Key name: "api-key"
   - Schema URL: Your GoalGPT API URL (e.g., `https://your-api.example.com/openapi.json`)
   - Or, paste the OpenAPI schema directly
   - Supported endpoints include:
     - GET `/goals` to list all goals
     - GET `/goals/{goal_id}` to retrieve a single goal
     - POST `/goals` to create a new goal
     - PATCH `/goals/{goal_id}` to update a goal
     - DELETE `/goals/{goal_id}` to delete a goal
     - GET `/gpt/goals` as a simplified tool-calling stub

## Example Interactions

Once set up, users can interact with the GPT using natural language:

- "Show me all my goals"
- "Create a new goal to learn React"
- "Mark my React learning goal as in progress"
- "Delete the goal about buying a car"
- "Create a sub-goal under my React learning goal to build a portfolio project"