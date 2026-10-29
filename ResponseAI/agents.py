from pathlib import Path
import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import get_websearch, scrape_url

# Load .env from module directory
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Model setup
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    # Check if OPENAI_API_KEY is available as fallback
    api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key or "placeholder_key",
    temperature=0.7
)

# Agent 1: Search Agent
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[get_websearch],
        system_prompt=(
            "You are a skilled web research agent. "
            "Use the get_websearch tool to find accurate, up-to-date information on the topic. "
            "Always include the discovered source URLs and summaries in your response."
        )
    )

# Agent 2: Reader Agent
def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url],
        system_prompt=(
            "You are an analytical reader agent. "
            "Analyze the search results, pick the single most relevant URL, "
            "call the scrape_url tool on it to read the full page, and summarize the deep insights found."
        )
    )

# Agent 3: Writer Chain
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, concise, well-structured and insightful reports."),
    ("human", """Write a detailed research report on the topic given below.

Topic: {topic}

Research Gathered:
{research}

Structure the report with the following markdown headers:
## Introduction
## Key Findings
(Provide a minimum of 3 well-defined, explained bullet points or sub-sections)
## Conclusion
## Sources
(List all URLs found in the research)

Be detailed, factual, and professional."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()

# Agent 4: Critic Chain
critic_prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific in your evaluation."),
    ("human", """Review the research report below and evaluate it strictly.

Report: {report}

Respond in this exact format:
Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One Line Verdict:
..."""),
])

critic_chain = critic_prompt_template | llm | StrOutputParser()
# Alias for backwards compatibility with pipeline.py imports
critic_prompt = critic_chain
