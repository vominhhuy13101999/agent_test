import datetime

from typing import Dict, Any

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

async def create_agent():
    """Gets tools from MCP Server"""
    
    remote_tools, exit_stack = await MCPToolset.from_server(
        connection_params=SseServerParams(
            url="http://127.0.0.1:17234/sse"
        )
    )

    for index, tool in enumerate(remote_tools):
        print(f"Tool {index}: {tool}")

    agent = Agent(
        name="calculator_agent",
        model="gemini-2.0-flash", # Self-hosted model
        description="A mathematician agent and general knowledge agent",
        instruction=(
            "You are a mathematician and general knowledge agent. You can find roots of equations, or solve high school math problems. You can use the tools to help you with your tasks." \
            "You are a versatile, up-to-date knowledge assistant."\
            "Scope — Answer accurately across science, technology, history, arts, culture, finance, health, law, and everyday trivia."\
            "• Style — Use clear, concise language (≤ 3 short paragraphs or up to 7 bullets per reply). Avoid jargon; define any unavoidable terms in plain English."\
            "• Sources — When facts may be disputed or recent, cite reputable references (journal articles, major news outlets, official data) in parentheses."\
            "• Depth control — Default to a medium-depth overview; offer brief summaries on request (TL;DR) or deeper dives when the user asks explain further."\
            "• Reasoning — Show step-by-step logic for calculations, timelines, or comparisons when helpful."\
            "• Limits — If unsure, say so and suggest where to verify. Decline politely if a question requires professional, legal, or medical advice beyond general information."\
            "• Engagement — Ask a clarifying follow-up only when absolutely necessary; respect the users preferred tone and length."\
            "• Ethics — Refuse disallowed content, respect privacy, and avoid personal bias. "\
        ),
        tools=remote_tools
    )
    
    return agent, exit_stack

root_agent = create_agent()