import asyncio
from typing import Optional
from contextlib import AsyncExitStack
from dotenv import load_dotenv
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import openai

load_dotenv()  # Load environment variables from .env

openai.api_key = os.getenv("OPENAI_API_KEY")


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server."""
        if not server_script_path.endswith(".py"):
            raise ValueError("Server script must be a .py")

        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using OpenAI GPT-4 and available MCP tools."""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query}
        ]

        tool_response = await self.session.list_tools()
        openai_tools = []
        tool_map = {}

        for tool in tool_response.tools:
            tool_def = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            }
            openai_tools.append(tool_def)
            tool_map[tool.name] = tool

        # First request to GPT-4
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=messages,
            tools=openai_tools,
            tool_choice="auto"
        )

        finish_reason = response.choices[0].finish_reason
        message = response.choices[0].message

        # Handle tool call
        if finish_reason == "tool_calls":
            tool_call = message.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = tool_call.function.arguments

            # Execute the tool via MCP
            result = await self.session.call_tool(tool_name, eval(tool_args))  # ⚠️ safe args parsing in production

            messages.append(message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result.content
            })

            # Get the final response from GPT-4
            final_response = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                messages=messages
            )
            return final_response.choices[0].message.content.strip()

        return message.get("content", "").strip()

    async def chat_loop(self):
        """Run an interactive chat loop."""
        try:
            query = ""  # Put the query here or modify for stdin if needed
            if query.lower() == 'quit':
                return

            response = await self.process_query(query)
            print("\n" + response)

        except Exception as e:
            print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources."""
        await self.exit_stack.aclose()
