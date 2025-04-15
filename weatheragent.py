# import json
# import requests
# import os
# from dotenv import load_dotenv
# from openai import OpenAI

# # Load environment variables
# load_dotenv()

# # Initialize Groq client
# client = OpenAI(
#     base_url="https://api.groq.com/openai/v1",
#     api_key=os.getenv("GROQ_API_KEY")
# )

# # Tools
# def get_weather(city: str):
#     print("🔨 Tool Called: get_weather", city)
#     url = f"https://wttr.in/{city}?format=%C+%t"
#     response = requests.get(url)
#     if response.status_code == 200:
#         return f"The weather in {city} is {response.text}."
#     return "Something went wrong"

# def run_command(command):
#     print("🔨 Tool Called: run_command", command)
#     result = os.system(command)
#     return f"Command executed with status: {result}"

# available_tools = {
#     "get_weather": {
#         "fn": get_weather,
#         "description": "Takes a city name as an input and returns the current weather for the city"
#     },
#     "run_command": {
#         "fn": run_command,
#         "description": "Takes a command as input to execute on system and returns output"
#     }
# }

# # System Prompt
# system_prompt = """
# You are a helpful AI Assistant specialized in resolving user queries.
# You work in start, plan, action, observe mode.

# For the given user query and available tools:
# - Plan the step-by-step execution.
# - Select the relevant tool from the available tools.
# - Perform an action to call the tool.
# - Wait for the observation and based on the observation from the tool call, resolve the user query.

# Rules:
# - Follow the Output JSON Format.
# - Always perform one step at a time and wait for the next input.
# - Carefully analyze the user query.

# Output JSON Format:
# {
#     "step": "string",
#     "content": "string",
#     "function": "The name of function if the step is action",
#     "input": "The input parameter for the function"
# }

# Available Tools:
# - get_weather: Takes a city name as input and returns current weather
# - run_command: Takes a command as input to execute and returns the output

# Example:
# User Query: What is the weather of new york?
# Output: { "step": "plan", "content": "The user is interested in weather data of new york" }
# Output: { "step": "plan", "content": "From the available tools I should call get_weather" }
# Output: { "step": "action", "function": "get_weather", "input": "new york" }
# Output: { "step": "observe", "output": "12 Degree Cel" }
# Output: { "step": "output", "content": "The weather for new york seems to be 12 degrees." }
# """

# # Message History
# messages = [
#     { "role": "system", "content": system_prompt }
# ]

# # Main loop
# while True:
#     user_query = input("> ")
#     messages.append({ "role": "user", "content": user_query })

#     while True:
#         response = client.chat.completions.create(
#             model="llama-3.3-70b-versatile",  # or "mixtral-8x7b-32768" depending on availability
#             response_format={"type": "json_object"},
#             messages=messages
#         )

#         parsed_output = json.loads(response.choices[0].message.content)
#         messages.append({ "role": "assistant", "content": json.dumps(parsed_output) })

#         if parsed_output.get("step") == "plan":
#             print(f"🧠: {parsed_output.get('content')}")
#             continue

#         if parsed_output.get("step") == "action":
#             tool_name = parsed_output.get("function")
#             tool_input = parsed_output.get("input")

#             if available_tools.get(tool_name):
#                 output = available_tools[tool_name]["fn"](tool_input)
#                 messages.append({
#                     "role": "assistant",
#                     "content": json.dumps({ "step": "observe", "output": output })
#                 })
#                 continue

#         if parsed_output.get("step") == "output":
#             print(f"🤖: {parsed_output.get('content')}")
#             break
import json
import requests
import os
import datetime
import re
import webbrowser
import time
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize Groq client
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

# Tool Functions
def get_weather(city):
    """Get current weather for a specified city."""
    print(f"🔨 Tool Called: get_weather for {city}")
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."
    return "Unable to fetch weather data."

def run_command(command):
    """Execute a system command and return the result."""
    print(f"🔨 Tool Called: run_command {command}")
    try:
        import subprocess
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return f"Command output: {result.stdout}\nErrors: {result.stderr}\nExit code: {result.returncode}"
    except Exception as e:
        return f"Error executing command: {str(e)}"

def set_reminder(task, time_str):
    """Set a reminder for a specific task at a specific time."""
    print(f"🔨 Tool Called: set_reminder for {task} at {time_str}")
    
    # In a real implementation, this would integrate with a notification system
    # Here we'll just simulate storing the reminder
    current_time = datetime.datetime.now()
    
    try:
        # Parse the time string
        reminder_time = parse_time_string(time_str, current_time)
        time_diff = reminder_time - current_time
        
        if time_diff.total_seconds() <= 0:
            return f"Cannot set reminder in the past. The time {time_str} has already passed."
        
        # Format for display
        formatted_time = reminder_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # In a real implementation, you would schedule this reminder
        # For demo purposes, just return confirmation
        return f"Reminder set for '{task}' at {formatted_time}."
    except ValueError as e:
        return f"Error setting reminder: {str(e)}"

def parse_time_string(time_str, current_time):
    """Helper function to parse various time formats."""
    # Try to parse explicit time
    time_formats = [
        "%H:%M", "%I:%M %p", "%Y-%m-%d %H:%M", 
        "%d/%m/%Y %H:%M", "%m/%d/%Y %H:%M"
    ]
    
    for fmt in time_formats:
        try:
            parsed_time = datetime.datetime.strptime(time_str, fmt)
            # If only time was provided (not date), use today's date
            if fmt in ["%H:%M", "%I:%M %p"]:
                parsed_time = current_time.replace(
                    hour=parsed_time.hour,
                    minute=parsed_time.minute,
                    second=0,
                    microsecond=0
                )
            return parsed_time
        except ValueError:
            continue
    
    # Try to parse relative time
    if "minutes" in time_str or "mins" in time_str or "min" in time_str:
        match = re.search(r'(\d+)\s*(minutes|mins|min)', time_str)
        if match:
            minutes = int(match.group(1))
            return current_time + datetime.timedelta(minutes=minutes)
    
    if "hours" in time_str or "hour" in time_str or "hr" in time_str or "hrs" in time_str:
        match = re.search(r'(\d+)\s*(hours|hour|hr|hrs)', time_str)
        if match:
            hours = int(match.group(1))
            return current_time + datetime.timedelta(hours=hours)
    
    # Handle special cases
    if "tomorrow" in time_str.lower():
        tomorrow = current_time + datetime.timedelta(days=1)
        if "at" in time_str.lower():
            time_part = time_str.lower().split("at")[1].strip()
            try:
                time_obj = datetime.datetime.strptime(time_part, "%H:%M")
                return tomorrow.replace(hour=time_obj.hour, minute=time_obj.minute, second=0, microsecond=0)
            except ValueError:
                pass
        return tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)  # Default to 9 AM
    
    if time_str.lower() in ["today", "this evening"]:
        return current_time.replace(hour=18, minute=0, second=0, microsecond=0)
    
    raise ValueError(f"Could not parse time format: {time_str}")

def search_web(query):
    """Search the web for information on a topic."""
    print(f"🔨 Tool Called: search_web for {query}")
    
    # In a real implementation, this would use a search API
    # For demonstration, we'll simulate a search result
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    if( webbrowser.open(search_url)):
        return f"I've opened a search for '{query}' in your web browser."
    else:
    # Option 1: Return the URL for the user to click
        return f"I've prepared a search for '{query}'. You can view the results at: {search_url}"
    
    # Option 2: If allowed to open browser:
    # webbrowser.open(search_url)
    # return f"I've opened a search for '{query}' in your web browser."

def get_time(location=None):
    """Get the current time, optionally for a specific location."""
    print(f"🔨 Tool Called: get_time for {location if location else 'local'}")
    
    if not location:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        return f"The current local time is {current_time}."
    else:
        # In a real implementation, use a timezone API
        # For demo, we'll simulate with a placeholder
        return f"To get the time in {location}, I would need to use a timezone API, which isn't implemented yet."

def create_todo(task):
    """Add a task to a to-do list."""
    print(f"🔨 Tool Called: create_todo for {task}")
    
    # In a real implementation, this would save to a file or database
    # For demo purposes, let's pretend we've added it
    return f"Added to your to-do list: {task}"

def get_todos():
    """Retrieve the current to-do list."""
    print("🔨 Tool Called: get_todos")
    
    # In a real implementation, this would read from a file or database
    # For demo purposes, return a placeholder
    return "Your to-do list functionality is set up but no storage is implemented yet. Items won't persist between sessions."

def send_email(to, subject, body):
    """Send an email to a recipient."""
    print(f"🔨 Tool Called: send_email to {to}")
    
    # In a real implementation, this would use SMTP or an email API
    # For demo purposes, just confirm the details
    return f"Email prepared to: {to}\nSubject: {subject}\nBody: {body}\n\nNote: This is a simulation. No actual email was sent."

def calculate(expression):
    """Evaluate a mathematical expression."""
    print(f"🔨 Tool Called: calculate {expression}")
    
    try:
        # Security note: eval can be dangerous if not properly sanitized
        # For a real application, use a safer math evaluation library
        if re.match(r'^[\d\+\-\*\/\(\)\.\s]*$', expression):
            result = eval(expression)
            return f"The result of {expression} is {result}"
        else:
            return "I can only evaluate basic mathematical expressions for security reasons."
    except Exception as e:
        return f"Error in calculation: {str(e)}"

def get_news(category=None):
    """Get the latest news, optionally filtered by category."""
    print(f"🔨 Tool Called: get_news for category {category if category else 'general'}")
    
    # In a real implementation, this would use a news API
    # For demo purposes, return a placeholder
    if category:
        return f"To get news about {category}, I would need to connect to a news API, which isn't implemented yet."
    else:
        return "To get the latest news, I would need to connect to a news API, which isn't implemented yet."

def play_music(song_or_playlist):
    """Play music or a playlist."""
    print(f"🔨 Tool Called: play_music for {song_or_playlist}")
    
    # In a real implementation, this would integrate with a music service API
    # For demo purposes, return a placeholder
    return f"I would play '{song_or_playlist}' if I had access to a music service API. This feature is a placeholder."

def translate_text(text, target_language):
    """Translate text to another language."""
    print(f"🔨 Tool Called: translate_text to {target_language}")
    
    # In a real implementation, this would use a translation API
    # For demo purposes, return a placeholder
    return f"To translate '{text}' to {target_language}, I would need to connect to a translation API, which isn't implemented yet."

def get_directions(start, destination):
    """Get directions from one location to another."""
    print(f"🔨 Tool Called: get_directions from {start} to {destination}")
    
    # In a real implementation, this would use a maps/directions API
    # For demo purposes, return a placeholder
    maps_url = f"https://www.google.com/maps/dir/{start.replace(' ', '+')}/{destination.replace(' ', '+')}"
    return f"I've prepared directions from {start} to {destination}. You can view them at: {maps_url}"

def convert_units(value, from_unit, to_unit):
    """Convert between different units of measurement."""
    print(f"🔨 Tool Called: convert_units {value} from {from_unit} to {to_unit}")
    
    # This is a simplified version, a real implementation would need more comprehensive unit handling
    unit_conversions = {
        # Length
        ("meters", "feet"): lambda x: x * 3.28084,
        ("feet", "meters"): lambda x: x * 0.3048,
        ("kilometers", "miles"): lambda x: x * 0.621371,
        ("miles", "kilometers"): lambda x: x * 1.60934,
        ("inches", "centimeters"): lambda x: x * 2.54,
        ("centimeters", "inches"): lambda x: x * 0.393701,
        
        # Weight/Mass
        ("kilograms", "pounds"): lambda x: x * 2.20462,
        ("pounds", "kilograms"): lambda x: x * 0.453592,
        ("grams", "ounces"): lambda x: x * 0.035274,
        ("ounces", "grams"): lambda x: x * 28.3495,
        
        # Temperature
        ("celsius", "fahrenheit"): lambda x: x * 9/5 + 32,
        ("fahrenheit", "celsius"): lambda x: (x - 32) * 5/9,
        
        # Volume
        ("liters", "gallons"): lambda x: x * 0.264172,
        ("gallons", "liters"): lambda x: x * 3.78541,
        ("milliliters", "fluid ounces"): lambda x: x * 0.033814,
        ("fluid ounces", "milliliters"): lambda x: x * 29.5735,
    }
    
    try:
        value = float(value)
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        conversion = unit_conversions.get((from_unit, to_unit))
        if conversion:
            result = conversion(value)
            return f"{value} {from_unit} is equal to {result:.4f} {to_unit}"
        else:
            return f"I don't know how to convert from {from_unit} to {to_unit}."
    except ValueError:
        return "Please provide a valid numerical value for conversion."
    except Exception as e:
        return f"Error during conversion: {str(e)}"

# Dictionary of available tools
available_tools = {
    "get_weather": {
        "fn": get_weather,
        "description": "Takes a city name as input and returns the current weather",
        "parameters": ["city"]
    },
    "run_command": {
        "fn": run_command,
        "description": "Takes a command to execute on the system and returns output (use cautiously)",
        "parameters": ["command"]
    },
    "set_reminder": {
        "fn": set_reminder,
        "description": "Takes a task and time as input to set a reminder",
        "parameters": ["task", "time_str"]
    },
    "search_web": {
        "fn": search_web,
        "description": "Searches the web for information on a given query",
        "parameters": ["query"]
    },
    "get_time": {
        "fn": get_time,
        "description": "Gets the current time, optionally for a specific location",
        "parameters": ["location"]
    },
    "create_todo": {
        "fn": create_todo,
        "description": "Adds a task to a to-do list",
        "parameters": ["task"]
    },
    "get_todos": {
        "fn": get_todos,
        "description": "Retrieves the current to-do list",
        "parameters": []
    },
    "send_email": {
        "fn": send_email,
        "description": "Sends an email to a recipient with a subject and body",
        "parameters": ["to", "subject", "body"]
    },
    "calculate": {
        "fn": calculate,
        "description": "Evaluates a mathematical expression",
        "parameters": ["expression"]
    },
    "get_news": {
        "fn": get_news,
        "description": "Gets the latest news, optionally filtered by category",
        "parameters": ["category"]
    },
    "play_music": {
        "fn": play_music,
        "description": "Plays music or a playlist",
        "parameters": ["song_or_playlist"]
    },
    "translate_text": {
        "fn": translate_text,
        "description": "Translates text to another language",
        "parameters": ["text", "target_language"]
    },
    "get_directions": {
        "fn": get_directions,
        "description": "Gets directions from one location to another",
        "parameters": ["start", "destination"]
    },
    "convert_units": {
        "fn": convert_units,
        "description": "Converts between different units of measurement",
        "parameters": ["value", "from_unit", "to_unit"]
    }
}

# Enhanced system prompt
system_prompt = """
You are SUMATI👱‍♀️ an advanced AI assistant designed to help with daily tasks. You work in a systematic way: plan, action, observe, output.

For any user query:
1. First, plan your approach by understanding what the user needs.
2. Select the most appropriate tool from your available tools, or determine if this requires a custom approach.
3. Take one action at a time, calling the necessary tool with the right parameters.
4. Observe the results of each action before proceeding.
5. Provide a helpful, concise response to the user based on all information gathered.

If a user's request doesn't match an existing tool exactly:
- Break down complex tasks into simpler steps that can be handled by your tools
- Ask the user for any missing information needed to complete the task
- Explain clearly what you need and why
- Be creative in combining tools to fulfill unusual requests

Very Important Rules for Using Tools:
- For all tool functions, provide parameters as key-value pairs in the "input" field
- Always use the exact parameter names specified for each tool
- Do not add extra parameters that are not defined for the tool
- Check the available_tools dictionary for the correct parameter names for each tool

Tool Parameter Reference:
- get_weather: {"city": "city_name"}
- run_command: {"command": "command_string"}
- set_reminder: {"task": "task_description", "time_str": "time_string"}
- search_web: {"query": "search_query"}
- get_time: {"location": "location_name"} (location is optional)
- create_todo: {"task": "task_description"}
- get_todos: {} (no parameters needed)
- send_email: {"to": "email_address", "subject": "email_subject", "body": "email_body"}
- calculate: {"expression": "math_expression"}
- get_news: {"category": "news_category"} (category is optional)
- play_music: {"song_or_playlist": "music_name"}
- translate_text: {"text": "text_to_translate", "target_language": "language_name"}
- get_directions: {"start": "starting_location", "destination": "ending_location"}
- convert_units: {"value": "numeric_value", "from_unit": "original_unit", "to_unit": "target_unit"}

Output JSON Format:
{
    "step": "string",  // One of: "plan", "action", "observe", "output"
    "content": "string",  // Your thoughts or final response
    "function": "string",  // The name of function if the step is action
    "input": {"param1": "value1", "param2": "value2"}  // The input parameters for the function
}
"""

# Message History
messages = [
    {"role": "system", "content": system_prompt}
]

# Main loop
def main():
    print("👱‍♀️SUMATI is ready! Type 'exit' to quit.")
    
    while True:
        user_query = input("\n👱‍♀️ > ")
        
        if user_query.lower() in ['exit', 'quit', 'bye']:
            print("🤖 Goodbye! Have a great day!")
            break
            
        messages.append({"role": "user", "content": user_query})
        
        # Handle the conversation with the AI
        handle_conversation(user_query)

def handle_conversation(user_query):
    try:
        while True:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Use your preferred model
                response_format={"type": "json_object"},
                messages=messages
            )
            
            response_content = response.choices[0].message.content
            
            try:
                parsed_output = json.loads(response_content)
                messages.append({"role": "assistant", "content": json.dumps(parsed_output)})
                
                # Process based on the step
                if parsed_output.get("step") == "plan":
                    print(f"🧠 Planning: {parsed_output.get('content')}")
                    continue
                    
                elif parsed_output.get("step") == "action":
                    tool_name = parsed_output.get("function")
                    tool_input = parsed_output.get("input")
                    
                    if tool_name in available_tools:
                        tool_fn = available_tools[tool_name]["fn"]
                        
                        # Handle function input correctly
                        try:
                            if isinstance(tool_input, dict):
                                # Extract the expected parameters
                                expected_params = available_tools[tool_name]["parameters"]
                                
                                # Filter to only include expected parameters
                                filtered_params = {k: v for k, v in tool_input.items() if k in expected_params}
                                
                                # Call function with keyword arguments
                                output = tool_fn(**filtered_params)
                            else:
                                # If a string was provided instead of a dict, try to adapt
                                if len(available_tools[tool_name]["parameters"]) == 1:
                                    # If function expects only one parameter, pass the input directly
                                    output = tool_fn(tool_input)
                                else:
                                    # Otherwise, inform about incorrect format
                                    output = f"Error: Tool '{tool_name}' expects parameters as a dictionary, but received: {tool_input}"
                                
                            print(f"🔧 Using tool: {tool_name}")
                            
                        except TypeError as e:
                            # Catch parameter mismatch errors
                            output = f"Error using tool '{tool_name}': {str(e)}. Please check parameter names."
                        except Exception as e:
                            output = f"Error using tool '{tool_name}': {str(e)}"
                        
                        # Add the observation to messages
                        messages.append({
                            "role": "assistant",
                            "content": json.dumps({"step": "observe", "output": output})
                        })
                        continue
                    else:
                        error_msg = f"Tool '{tool_name}' is not available."
                        messages.append({
                            "role": "assistant",
                            "content": json.dumps({"step": "observe", "output": error_msg})
                        })
                        continue
                        
                elif parsed_output.get("step") == "output":
                    print(f"👱‍♀️ {parsed_output.get('content')}")
                    break
                    
                else:
                    print(f"👱‍♀️ {parsed_output.get('content', 'I encountered an issue processing your request.')}")
                    break
                    
            except json.JSONDecodeError:
                print("👱‍♀️ I encountered an error processing the response. Let me try again.")
                # Add an error message to help the model correct itself
                messages.append({
                    "role": "assistant", 
                    "content": json.dumps({
                        "step": "observe", 
                        "output": "Error: Invalid JSON format. Please ensure your response is valid JSON."
                    })
                })
                continue
                
    except Exception as e:
        print(f"👱‍♀️ Sorry, I encountered an error: {str(e)}")

if __name__ == "__main__":
    main()