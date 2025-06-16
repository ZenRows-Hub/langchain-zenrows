"""
Agent that scrapes news sites and provides summaries in markdown format.
"""

import os
from langchain_zenrows import ZenRowsUniversalScraper
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# Set API keys
os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"
os.environ["OPENAI_API_KEY"] = "<YOUR_OPENAI_API_KEY>"

# Initialize components
llm = ChatOpenAI(model="gpt-4o-mini")
zenrows_tool = ZenRowsUniversalScraper()

# Create agent
agent = create_react_agent(llm, [zenrows_tool])

# Task: Summarize latest tech news
result = agent.invoke(
    {
        "messages": [
            "Go to TechCrunch.com, scrape the homepage in markdown format, and provide a summary of the top 5 technology stories with their headlines and brief descriptions."
        ]
    }
)

print("Tech News Summary:")
for message in result["messages"]:
    print(f"{message.content}")
