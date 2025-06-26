import os
import inspect
from dotenv import load_dotenv
import re

# Import Content, the correct object for holding a role
from vertexai.generative_models import Content, GenerativeModel, Tool, Part, FunctionDeclaration
import vertexai
PROJECT_ID = "google-cloud-project-id"  
REGION = "google-cloud-region"     

import tools

class RestaurantAgent:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        

        self.gemini_tools = self._get_gemini_tool_definitions()
        self.model = GenerativeModel(model_name, tools=self.gemini_tools)
        
        self.last_booking = None
        self.chat = self.model.start_chat(history=[self._get_initial_guidance()])

    def _get_gemini_tool_definitions(self) -> list:
        """Dynamically creates Gemini-compatible tool definitions from our tools.py file."""
        tool_declarations = []
        for name, func in inspect.getmembers(tools, inspect.isfunction):
            if not name.startswith("_"):
                func_declaration = FunctionDeclaration(
                    name=name,
                    description=inspect.getdoc(func),
                    parameters=self._get_params_from_signature(func)
                )
                tool_declarations.append(func_declaration)
        return [Tool(function_declarations=tool_declarations)]

    def _get_params_from_signature(self, func) -> dict:
        """A helper to convert a Python function's signature into a JSON Schema for the Gemini API."""
        sig = inspect.signature(func)
        properties = {}
        required = []
        for name, param in sig.parameters.items():
            param_type = "STRING"
            if param.annotation == int: param_type = "INTEGER"
            elif param.annotation == float: param_type = "NUMBER"
            properties[name] = {"type": param_type}
            if param.default == inspect.Parameter.empty: required.append(name)
        return {"type": "OBJECT", "properties": properties, "required": required}

    def _get_initial_guidance(self) -> Content:
        """
        Creates the definitive system guidance prompt to ensure robust and helpful behavior.
        """
        guidance_text = (
            
            "You are a highly intelligent and precise restaurant reservation assistant for 'GoodFoods'. "
            "Your primary goal is to help users by strictly following these rules:\n"
            "1.  **Deconstruct Tasks:** Break down user requests into logical steps. If a user asks to find a restaurant and book it, first find the restaurant, present the options, and only then ask for booking details.\n"
            "2.  **Validate Parameters Before Tool Use:** Before calling any tool, you MUST check the user's input for validity. If a parameter is nonsensical (e.g., party size of -2 or 0), you MUST ask the user for a correction. You are FORBIDDEN from correcting the input yourself.\n"
            "3.  **Handle Dates Explicitly:** You CANNOT process relative dates like 'today' or 'tomorrow'. If a user mentions a relative date, you MUST ask them to provide a specific date (e.g., 'June 20th').\n"
            "4.  **Handle Failed Searches:** If a `search_restaurants` call with a specific location returns no results, you MUST immediately use the `list_known_locations` tool to show the user valid location options.\n"
            "5.  **Handle Changes/Cancellations:** To change a reservation, you must first call `cancel_reservation` and then help the user make a new booking. Use details from the last successful booking for the cancellation.\n"
            "6.  **Handle Complex Comparisons:** You cannot directly compare two items (e.g., 'which is better'). State this limitation, then offer to provide the data for each item one by one.\n"
            "7.  **Handle Small Talk:** If the user engages in small talk or asks off-topic questions, respond conversationally without trying to use a tool.\n"
            "8.  **Pre-emptive Validation (CRITICAL):** Before calling any tool, you MUST validate the user's input. If a parameter is invalid (e.g., party size of -2), you MUST ask for a correction. You are FORBIDDEN from correcting input yourself.\n"
            "9.  **Time & Date Parsing (CRITICAL):** You are responsible for parsing time and dates. When a user gives a time (e.g., 'tomorrow at 9pm', 'June 23rd 8:00 PM'), you MUST convert it to a strict `HH:MM` format. Pass ONLY this `HH:MM` string to the tools. Do not include dates or other words in the time parameter.\n"
            "10.  **Restaurant Lists Formatting:** When presenting a list of restaurants, ALWAYS format the output as a markdown bullet list or table. For example:\n"
            "- Barbeque Nation: North Indian, BBQ | ₹1600 | ⭐ 4.7\n"
            "- Chianti: Italian | ₹1500 | ⭐ 4.7\n"
            "Do NOT use a single paragraph for lists. Use clear, line-by-line formatting for readability.\n"
        )
        return Content(role="user", parts=[Part.from_text(f"SYSTEM GUIDANCE: {guidance_text}")])

    def run(self, user_message: str):
        """
        The main execution loop. It sends messages, handles tool calls in a loop,
        manages state, and returns the final text response to the user.
        """
        print(f"👤 User: {user_message}")
        response = self.chat.send_message(user_message)

        while True:
            candidate = response.candidates[0]
            function_call_part = None
            
            for part in candidate.content.parts:
                if part.function_call:
                    function_call_part = part.function_call
                    break

            if function_call_part:
                tool_name = function_call_part.name
                tool_params = {key: value for key, value in function_call_part.args.items()}
                
                print(f"🤖 LLM wants to call tool: {tool_name} with params: {tool_params}")

                if hasattr(tools, tool_name):
                    tool_function = getattr(tools, tool_name)
                    try:
                        tool_result = tool_function(**tool_params)
                        if tool_name == 'create_reservation' and tool_result.get('status') == 'Success':
                            self.last_booking = tool_result.get('booking_details')
                            print(f"✅ State Updated: Last booking is now {self.last_booking}")
                        elif tool_name == 'cancel_reservation' and tool_result.get('status') == 'Success':
                            self.last_booking = None
                            print(f"🗑️ State Cleared: Last booking has been cancelled.")
                    except Exception as e:
                        tool_result = {"error": str(e)}
                else:
                    tool_result = {"error": f"Tool '{tool_name}' not found."}
                
                print(f"🛠️ Tool Result: {tool_result}")

                response = self.chat.send_message(
                    Part.from_function_response(name=tool_name, response={"content": tool_result})
                )
                continue
            else:
                final_text = "".join(part.text for part in candidate.content.parts if hasattr(part, 'text'))
                return final_text
