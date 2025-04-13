import json
import requests
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize Groq client
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

# Tools
def get_weather(city: str):
    print("🔨 Tool Called: get_weather", city)
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."
    return "Something went wrong"

def run_command(command):
    print("🔨 Tool Called: run_command", command)
    result = os.system(command)
    return f"Command executed with status: {result}"

available_tools = {
    "get_weather": {
        "fn": get_weather,
        "description": "Takes a city name as an input and returns the current weather for the city"
    },
    "run_command": {
        "fn": run_command,
        "description": "Takes a command as input to execute on system and returns output"
    }
}

# System Prompt
system_prompt = """
You are a helpful AI Assistant specialized in resolving user queries.
You work in start, plan, action, observe mode.

For the given user query and available tools:
- Plan the step-by-step execution.
- Select the relevant tool from the available tools.
- Perform an action to call the tool.
- Wait for the observation and based on the observation from the tool call, resolve the user query.

Rules:
- Follow the Output JSON Format.
- Always perform one step at a time and wait for the next input.
- Carefully analyze the user query.

Output JSON Format:
{
    "step": "string",
    "content": "string",
    "function": "The name of function if the step is action",
    "input": "The input parameter for the function"
}

Available Tools:
- get_weather: Takes a city name as input and returns current weather
- run_command: Takes a command as input to execute and returns the output

Example:
User Query: What is the weather of new york?
Output: { "step": "plan", "content": "The user is interested in weather data of new york" }
Output: { "step": "plan", "content": "From the available tools I should call get_weather" }
Output: { "step": "action", "function": "get_weather", "input": "new york" }
Output: { "step": "observe", "output": "12 Degree Cel" }
Output: { "step": "output", "content": "The weather for new york seems to be 12 degrees." }
"""

# Message History
messages = [
    { "role": "system", "content": system_prompt }
]

# Main loop
while True:
    user_query = input("> ")
    messages.append({ "role": "user", "content": user_query })

    while True:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # or "mixtral-8x7b-32768" depending on availability
            response_format={"type": "json_object"},
            messages=messages
        )

        parsed_output = json.loads(response.choices[0].message.content)
        messages.append({ "role": "assistant", "content": json.dumps(parsed_output) })

        if parsed_output.get("step") == "plan":
            print(f"🧠: {parsed_output.get('content')}")
            continue

        if parsed_output.get("step") == "action":
            tool_name = parsed_output.get("function")
            tool_input = parsed_output.get("input")

            if available_tools.get(tool_name):
                output = available_tools[tool_name]["fn"](tool_input)
                messages.append({
                    "role": "assistant",
                    "content": json.dumps({ "step": "observe", "output": output })
                })
                continue

        if parsed_output.get("step") == "output":
            print(f"🤖: {parsed_output.get('content')}")
            break
